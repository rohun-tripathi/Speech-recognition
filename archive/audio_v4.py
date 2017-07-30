import csv
import glob
import re
import os
from random import Random

from pydub import AudioSegment
from watson_developer_cloud import SpeechToTextV1

from datetime import datetime
import logging, sys

# Creds for gmail id
# IBM_PASSWORD = 'uQnccEAUC2CE'
# IBM_USERNAME = '8de9146e-c657-48d5-b4e2-cfdf5ad0fc4f'

# Creds for IBM id.
IBM_PASSWORD = 'uQnccEAUC2CE'
IBM_USERNAME = '8de9146e-c657-48d5-b4e2-cfdf5ad0fc4f'

USE_ONLY_TWO = False
USE_LAST_TWO_WORD = True

NOISE_THROUGH_OUT = True

if USE_ONLY_TWO :
    USE_LAST_TWO_WORD = True

if not USE_LAST_TWO_WORD:
    # Then noise through out is not supported.
    NOISE_THROUGH_OUT = False

NOISE_TYPE = "White"
OUT_TAG = "confidence" + "_" + NOISE_TYPE + "_" + "Youtube_Lecture_" + "NOISE_THROUGH_OUT" + "_LAST_TWO_WORDS"

##################### Clip Properties ##############

IGNORE_START_WORDS = 6
HIGH_CONF_THRESHOLD = 0.70
LOW_CONF_THRESHOLD = 0.5
TIME_BEFORE_FIRST_WORD = 2.5
TIME_AFTER_SECOND_WORD = 1.5

AUDIO_CHUNK_SIZE_SECONDS = 25
MIN_AUDIO_CHUNK_SIZE = 5


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
        logging.critical("Noise type not defined")
        print("Noise type not defined")
        sys.exit(0)
    return NOISE_TYPE, noise


class WordObject:
    def __init__(self, value, **kwargs):
        self.start_time = value['start_time']
        self.end_time = value['end_time']
        self.confidence = value["alternatives"][0]['confidence']
        self.word = value['alternatives'][0]['word']

        self.word_alternatives = []
        if kwargs.get("parent", True):
            for single_alternative in value["alternatives"]:
                self.word_alternatives.append(
                    WordObject({"start_time": self.start_time, "end_time": self.end_time,
                                "alternatives": [{"confidence": single_alternative["confidence"],
                                                  "word": single_alternative["word"]}]}, parent=False))


def save_to_chunks(file_name_list, chunk_input_folder, grouped_input, file_format):
    successful_chunk_file_list = []

    source_regex = r"(?<=" + re.escape(grouped_input) + r").+?(?=" + re.escape(file_format) + r")"
    for complete_file_name in file_name_list:
        try:
            k = complete_file_name.rfind(".")  # find the last occurrence of dot
            audio = AudioSegment.from_file(complete_file_name, complete_file_name[k + 1:])

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

            if audio.duration_seconds >= MIN_AUDIO_CHUNK_SIZE:
                audio.export(chunk_input_folder + extract_just_name + "_final_chunk_" + str(chunk_number) + '.wav',
                             format='wav')

            successful_chunk_file_list.append(complete_file_name)
        except Exception as e:
            logging.debug(str(e))
    return successful_chunk_file_list


def getTextFromSpeech(file_name):
    with open(file_name, 'rb') as audio_file:
        return speech_to_text.recognize(audio_file, content_type='audio/wav', timestamps=True,
                                        word_confidence=True, word_alternatives_threshold=0.001, continuous=True)


# noinspection PyBroadException
def transcribe_robustly(file_name):
    try:
        result = getTextFromSpeech(file_name)
    except Exception:
        try:
            result = getTextFromSpeech(file_name)
        except Exception:
            return {}

    return result


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
    res_start_time = [];
    res_end_time = [];
    res_confidence = [];
    res_word = [];
    for val in result_dict:
        res_start_time.append(val['start_time']);
        res_end_time.append(val['end_time']);
        res_confidence.append(val['alternatives'][0]['confidence']);
        res_word.append(val['alternatives'][0]['word']);

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





def prepare_for_user_study(user_study_input_data, audio_type, now, file_ending=".wav"):
    global gbl_rows, selected_rows

    study_output_folder = "user_study_output\\"
    file_list = glob.glob(user_study_input_data + "*" + file_ending)

    Random(4).shuffle(file_list)

    file_list = file_list[75:115]

    source_regex = r"(?<=" + re.escape(user_study_input_data) + r").+?(?=.wav)"

    break_execution = False

    for file_entry in file_list:
        try:
            if break_execution:
                break

            extract_just_name = re.findall(source_regex, file_entry)
            if len(extract_just_name) != 0:
                extract_just_name = extract_just_name[0]
            else:
                continue
            extract_just_name = extract_just_name + "_" + now
            user_study_function(file_entry, study_output_folder, extract_just_name, audio_type)

            logging.info("Done for : " + file_entry + " output : " + str(gbl_rows) + str(selected_rows))
            print("Done for : " + file_entry + " output : " + str(gbl_rows) + str(selected_rows))

            if len(gbl_rows) > 0:
                global_csv_writer.writerows(gbl_rows)
                gbl_rows = []

            if len(selected_rows) > 0:
                selected_csv_writer.writerows(selected_rows)
                selected_rows = []

        except Exception as e:
            logging.error(str(e))


if __name__ == '__main__':

    logging.basicConfig(filename='user_study_data.log', format='%(funcName)s : %(message)s', level=logging.INFO)

    speech_to_text = SpeechToTextV1(
        username=IBM_USERNAME,
        password=IBM_PASSWORD,
        x_watson_learning_opt_out=False
    )

    now = str(datetime.now().timestamp()).replace(".", "")
    file_layout = open("logs\\detailed_log_" + now + "_" + OUT_TAG + ".csv", "w", newline='')
    global_csv_writer = csv.writer(file_layout)
    gbl_rows = []
    selected_strings_layout = open("logs\\selected_log_" + now + "_" + OUT_TAG + ".csv", "w", newline='')
    selected_csv_writer = csv.writer(selected_strings_layout)
    selected_rows = []

    # Chunk input files. Required because 30 min files don't return.
    try:
        audio_property_list = [
            {"type": "lecture", "output": "user_study_output\\user_study_initial_output\\lecture\\",
             "input": "data_input\\lecture\\", "chunk": False},
            {"type": "movie", "output": "user_study_output\\user_study_initial_output\\movie\\",
             "input": "data_input\\movie\\", "chunk": True},
            {"type": "song", "output": "user_study_output\\user_study_initial_output\\song\\",
             "input": "data_input\\song\\", "chunk": False},
            {"type": "radio", "output": "user_study_output\\user_study_initial_output\\philip_marlowe\\",
             "input": "data_input\\philip_marlowe\\", "chunk": False}]

        for property in audio_property_list[:1]:
            chunk_location = property["output"]
            os.makedirs(chunk_location, exist_ok=True)

            chunking_required = property["chunk"]
            if chunking_required:

                if property["type"] == "song":
                    AUDIO_CHUNK_SIZE_SECONDS = 10
                else:
                    AUDIO_CHUNK_SIZE_SECONDS = 25

                original_un_chunked_data = property["input"]
                file_format = ".mp3"
                file_name_list = glob.glob(original_un_chunked_data + "*" + file_format)
                save_to_chunks(file_name_list, chunk_location, original_un_chunked_data, file_format)

            prepare_for_user_study(chunk_location, property["type"], now, file_ending=".wav")

    except Exception as e:
        logging.error(str(e))

    file_layout.close()
    selected_strings_layout.close()
