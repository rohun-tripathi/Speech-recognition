import re
import sys

from nltk.corpus import wordnet
from nltk.corpus import words
from pydub import AudioSegment
from watson_developer_cloud import SpeechToTextV1

from audio_v5 import CAPTCHA_TYPE, IBM_PASSWORD, IBM_USERNAME

# (v1) random numbers - max 8 numbers. crop the file.
# (v2) two words only - both words should be more than 5 chars long
# (v3) (a) full phrase with last two words with noise; (b) full phrase with full noise
# (v4) full phrase with full noise

MINIMUM_NUMBER_OF_CHAR = 4
USE_ONLY_TWO = False
USE_LAST_TWO_WORD = False
NOISE_THROUGH_OUT = False

if CAPTCHA_TYPE == "2":
    USE_ONLY_TWO = True
    USE_LAST_TWO_WORD = True
    NOISE_THROUGH_OUT = True
    MINIMUM_NUMBER_OF_CHAR = 5

elif CAPTCHA_TYPE == "3a":
    USE_ONLY_TWO = False
    USE_LAST_TWO_WORD = True
    NOISE_THROUGH_OUT = False

elif CAPTCHA_TYPE == "3b":
    USE_ONLY_TWO = False
    USE_LAST_TWO_WORD = True
    NOISE_THROUGH_OUT = True

elif CAPTCHA_TYPE == "4":
    # Flow changes, these do not matter
    pass

else:
    raise Exception("Unknown Version Number")

#################

OUTPUT_DATA_DETAILS_STAGE = "C:\\Users\\IBM_ADMIN\\speech_recognition\\data_output_details_stage\\"
OUTPUT_DATA_SELECTED = "C:\\Users\\IBM_ADMIN\\speech_recognition\\data_output_selected\\"
INPUT_CHUNK_STAGE = "C:\\Users\\IBM_ADMIN\\speech_recognition\\data_chunk_stage\\"
INPUT_DATA_STAGE = "C:\\Users\\IBM_ADMIN\\speech_recognition\\data_input_stage\\"

AUDIO_LOUDNESS_THRESHOLD = -11.44

NLTK_DICTIONARY = None
CUSTOM_DICTIONARY = None

NOISE_TYPE = "White"

AUDIO_CHUNK_SIZE_SECONDS = 25
MIN_AUDIO_CHUNK_SIZE_SECONDS = 5

HIGH_CONF_THRESHOLD = 0.70
LOW_CONF_THRESHOLD = 0.5

#################

speech_to_text = SpeechToTextV1(
    username=IBM_USERNAME,
    password=IBM_PASSWORD,
    x_watson_learning_opt_out=False
)


def get_noise():
    if NOISE_TYPE == "White":
        noise = AudioSegment.from_file("parameter_input\\noise.wav", format="wav")
    elif NOISE_TYPE == "school_corridor":
        noise = AudioSegment.from_file("parameter_input\\Chatter_In_School_Corridor_20.wav", format="wav")
    elif NOISE_TYPE == "child":
        noise = AudioSegment.from_file("parameter_input\\12_children_sound_effect_20.wav", format="wav")
    elif NOISE_TYPE == "train":
        noise = AudioSegment.from_file("parameter_input\\steam-train-daniel_simon_20.wav", format="wav")
    else:
        print("Noise type not defined")
        sys.exit(0)
    return NOISE_TYPE, noise


def check_word_confidence(predicted_word_list, original_word_list, audio_start_offset):
    for stt_object in original_word_list:
        if stt_object.confidence > HIGH_CONF_THRESHOLD and stt_object.length >= MINIMUM_NUMBER_OF_CHAR:
            stt_word = stt_object.word
            stt_start_time = stt_object.start_time - audio_start_offset
            stt_end_time = stt_object.end_time - audio_start_offset

            # Initialized to 0, to denote that the sst could not detect the required word
            detected_confidence = 0

            detected_confidence = \
                get_predicted_confidence(detected_confidence, stt_end_time, stt_start_time, stt_word,
                                         predicted_word_list)

            if detected_confidence < 0.5:
                return stt_word, True

    return None, False


class WordObject:
    def __init__(self, value, **kwargs):
        self.start_time = value['start_time']
        self.end_time = value['end_time']
        self.confidence = value["alternatives"][0]['confidence']
        self.word = value['alternatives'][0]['word']
        self.length = len(self.word)

        self.word_alternatives = []
        if kwargs.get("parent", True):
            for single_alternative in value["alternatives"]:
                self.word_alternatives.append(
                    WordObject({"start_time": self.start_time, "end_time": self.end_time,
                                "alternatives": [{"confidence": single_alternative["confidence"],
                                                  "word": single_alternative["word"]}]}, parent=False))

    def __str__(self):
        return str({"start_time": self.start_time, "end_time": self.end_time, "confidence": self.confidence,
                    "word": self.word, "length": self.length})


def save_to_chunks(file_name_list, chunk_input_folder, grouped_input):
    successful_chunk_file_list = []
    failed_chunk_file_list = []

    for complete_file_name in file_name_list:
        try:
            k = complete_file_name.rfind(".")  # find the last occurrence of dot
            file_format = complete_file_name[k + 1:]

            audio = AudioSegment.from_file(complete_file_name, file_format)
            if audio.frame_rate < 16000:
                raise Exception("Frame Rate below 16000 " + complete_file_name + " frame rate " + str(
                    audio.frame_rate) + ". This file has to stop as IBM needs minimum 16000.")

            source_regex = r"(?<=" + re.escape(grouped_input) + r").+?(?=" + "." + re.escape(file_format) + r")"
            extract_just_name = re.findall(source_regex, complete_file_name)

            if len(extract_just_name) != 0:
                extract_just_name = extract_just_name[0]
            else:
                from datetime import datetime
                now = datetime.now()
                extract_just_name = "file_" + str(now.hour) + "_" + str(now.second)

            chunk_number = 0
            while audio.duration_seconds >= AUDIO_CHUNK_SIZE_SECONDS:
                chunk = audio[:AUDIO_CHUNK_SIZE_SECONDS * 1000]
                audio = audio[AUDIO_CHUNK_SIZE_SECONDS * 1000:]

                chunk.export(chunk_input_folder + extract_just_name + "_chunk_" + str(chunk_number) + '.wav',
                             format='wav')
                chunk_number += 1

            if audio.duration_seconds >= MIN_AUDIO_CHUNK_SIZE_SECONDS:
                audio.export(chunk_input_folder + extract_just_name + "_final_chunk_" + str(chunk_number) + '.wav',
                             format='wav')

            successful_chunk_file_list.append(complete_file_name)
        except Exception as e:
            failed_chunk_file_list.append(complete_file_name)
            print(str(e))

    return successful_chunk_file_list, failed_chunk_file_list


def get_text_from_speech(file_name, extract_speaker):
    with open(file_name, 'rb') as audio_file:
        return speech_to_text.recognize(audio_file, content_type='audio/wav', timestamps=True,
                                        speaker_labels=extract_speaker,
                                        word_confidence=True, word_alternatives_threshold=0.01)


# noinspection PyBroadException
def transcribe_robustly(file_name, speakers=False):
    audio_file = AudioSegment.from_file(file_name, ".wav")
    if audio_file.frame_rate < 16000:
        error_message = "Frame Rate below 16000 . This file has to be stopped."
        print(error_message + " " + file_name + " frame rate " + str(audio_file.frame_rate))
        raise Exception(error_message)

    try:
        result = get_text_from_speech(file_name, speakers)
    except Exception:
        try:
            result = get_text_from_speech(file_name, speakers)
        except Exception:
            return {}

    return result


def merge_transcription_from_parts(word_objects):
    result_transcript = ""

    for word_object in word_objects:
        result_transcript += word_object.word + " "

    return result_transcript.strip(), word_objects[0].start_time, word_objects[-1].end_time


def get_word_list(result_dict):
    word_list = []
    for val in result_dict:
        word_list.append(WordObject(val))
    return word_list


def get_dict(result, tag="word_alternatives"):
    result_dict = []
    for utterance in result["results"]:
        if tag not in utterance:
            raise Exception("Unknown Value Exception. No Alternatives returned")
        for hypothesis in utterance[tag]:
            result_dict.append(hypothesis)
    return result_dict


def get_res_details(result_dict):
    res_start_time = []
    res_end_time = []
    res_confidence = []
    res_word = []
    for val in result_dict:
        res_start_time.append(val['start_time'])
        res_end_time.append(val['end_time'])
        res_confidence.append(val['alternatives'][0]['confidence'])
        res_word.append(val['alternatives'][0]['word'])

    return res_start_time, res_end_time, res_confidence, res_word


def lies_between_start_end(start_time, end_time, stt_start_time, stt_end_time):
    return (stt_start_time <= start_time <= stt_end_time) or (stt_start_time <= end_time <= stt_end_time) or (
        start_time < stt_start_time and stt_end_time < end_time)


def get_predicted_confidence(detected_confidence, stt_end_time, stt_start_time, stt_word, word_list):
    for word_object in word_list:
        for alternative in word_object.word_alternatives:
            if alternative.word == stt_word:
                if lies_between_start_end(alternative.start_time, alternative.end_time, stt_start_time, stt_end_time):
                    return alternative.confidence
    return detected_confidence


# Speaker #################################################


class Speaker:
    def __init__(self, speaker_entry):
        self.start = speaker_entry["from"]
        self.end = speaker_entry["to"]
        self.number = speaker_entry["speaker"]
        self.confidence = speaker_entry["confidence"]

    def __str__(self):
        return str({"start": self.start, "end": self.end, "confidence": self.confidence,
                    "number": self.number})


def is_speaker_unique(speaker_list, start, end):
    if speaker_list is None or len(speaker_list) == 0:
        return True

    unique_speakers = set()
    for speaker in speaker_list:
        if speaker.end <= start or speaker.start >= end:
            continue

        unique_speakers.add(speaker.number)

    return len(unique_speakers) < 2


def get_speaker_list(result):
    speaker_list = []
    if "speaker_labels" not in result:
        return speaker_list

    for speaker_entry in result["speaker_labels"]:
        speaker_list.append(Speaker(speaker_entry))

    return speaker_list


def is_length_within_limits(word_list):
    """Checks the clip and word length. For just two words, 1 sec was too less and valid cases were missed."""

    transcription, start, end = merge_transcription_from_parts(word_list)

    if len(word_list) == 2:
        if end - start > 2:
            print("Clip Length of two words more than maximum")
            return False

    else:
        if end - start > 4:
            print("Clip Length of full phrase more than maximum")
            return False
        elif len(word_list) > 7:
            print("Word Length of full phrase more than maximum")
            return False
        elif len(word_list) != 2 and len(word_list) < 4:
            print("Word Length of full phrase less than minimum")
            return False

    return True


def is_dictionary_word(word_object):
    global NLTK_DICTIONARY, CUSTOM_DICTIONARY
    if NLTK_DICTIONARY is None:
        NLTK_DICTIONARY = set(words.words())

    if NLTK_DICTIONARY.__contains__(word_object.word):
        return True

    if CUSTOM_DICTIONARY is None:
        with open("parameter_input\\english_words.txt") as word_file:
            CUSTOM_DICTIONARY = set(word.strip().lower() for word in word_file)

    if CUSTOM_DICTIONARY.__contains__(word_object.word):
        return True

    if wordnet.synsets(word_object.word):
        return True

    return False


def is_word_set_eligible(word_list):
    unique_words = set()

    for word_object in word_list:
        if not is_dictionary_word(word_object):
            return False
        unique_words.add(word_object.word)

    if len(unique_words) != len(word_list):
        # Words must be repeated
        return False

    return True


def check_and_reduce_volume_too_loud(file_entry):
    audio = AudioSegment.from_file(file_entry, format="wav")

    if audio.dBFS > AUDIO_LOUDNESS_THRESHOLD:
        value_above_threshold = audio.dBFS - AUDIO_LOUDNESS_THRESHOLD
        audio = audio - value_above_threshold
        audio.export(file_entry, format="wav")
