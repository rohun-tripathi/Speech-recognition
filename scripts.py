import function_library as func_lib
import json
from glob import glob
import logging


def test_speakers():
    file_name = "user_study_output\\user_study_initial_output\\lecture\\Elon_Musk_chunk_19.wav"

    result = func_lib.transcribe_robustly(file_name, True)

    speaker_list = func_lib.get_speaker_list(result)

    speaker_json = "; ".join(str(dummy_word) for dummy_word in speaker_list)
    json.dump(speaker_json, open("archive\\speaker_test.json", "w"))


def create_shell_for_crap_data():
    logging.basicConfig(filename="below_16000_file_names_removed.txt")

    source = "C:\\Users\\IBM_ADMIN\\Box Sync\\AudioCaptcha\\Code\\stt_code\\user_study_output\\user_study_initial_output\\podcast_lecture\\"

    file_list = glob(source + "*.wav")

    for file_name in file_list:
        audio_file = func_lib.AudioSegment.from_file(file_name, format="wav")
        if audio_file.frame_rate < 16000:
            logging.log(logging.CRITICAL, file_name)
            func_lib.AudioSegment.silent(duration=1, frame_rate=11025).export(file_name, format="wav")


if __name__ == '__main__':
    create_shell_for_crap_data()
