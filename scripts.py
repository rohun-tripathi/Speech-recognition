import function_library as func_lib
import json


def test_speakers():
    file_name = "user_study_output\\user_study_initial_output\\lecture\\Elon_Musk_chunk_19.wav"

    result = func_lib.transcribe_robustly(file_name, True)

    speaker_list = func_lib.get_speaker_list(result)

    speaker_json = "; ".join(str(dummy_word) for dummy_word in speaker_list)
    json.dump(speaker_json, open("archive\\speaker_test.json", "w"))


if __name__ == '__main__':
    test_speakers()
