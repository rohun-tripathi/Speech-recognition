import csv
import glob
import logging
import os
import re
from datetime import datetime
from random import Random

import global_constants

CAPTCHA_TYPE = "4"

##################

import function_library as func_lib
import word_list_format
import consecutive_words_format

OUT_TAG = "REFACTORED" + "_" + "PODCAST" + "_VERSION_" + CAPTCHA_TYPE

main_process_start_time = str(datetime.now()).replace(" ", "_").replace(":", "_").replace(".", "_")

# Logging
selected_csv_writer = None
global_csv_writer = None

logging.basicConfig(filename=os.path.join('process_logs', 'info_' + CAPTCHA_TYPE + '.log'), format='%(message)s',
                    level=logging.INFO)


def prepare_for_user_study(user_study_input_data, audio_type, time_now, file_ending=".wav"):
    file_list = glob.glob(user_study_input_data + "*" + file_ending)
    Random(4).shuffle(file_list)

    length_portion = int(len(file_list) / 20)
    if CAPTCHA_TYPE == "2":
        file_list = file_list[length_portion * 15: length_portion * 17]
    elif CAPTCHA_TYPE == "3b":
        file_list = file_list[length_portion * 17: length_portion * 19]
    elif CAPTCHA_TYPE == "4":
        file_list = file_list[length_portion * 19: length_portion * 20]
    elif CAPTCHA_TYPE == "3a":
        raise Exception("3a not generated anymore")
    else:
        raise Exception("Captcha Type not supported")

    # If further reduction in set is required.
    file_list = file_list[365:]

    gbl_rows = []
    selected_rows = []

    source_regex = r"(?<=" + re.escape(user_study_input_data) + r").+?(?=.wav)"

    # This can be improved
    study_output_folder = global_constants.OUTPUT_DATA_DETAILS_STAGE

    break_execution = False
    for file_index, file_entry in enumerate(file_list):
        try:
            if break_execution:
                break

            func_lib.check_and_reduce_volume_too_loud(file_entry)

            extract_just_name = re.findall(source_regex, file_entry)
            if len(extract_just_name) != 0:
                extract_just_name = extract_just_name[0]
            else:
                continue
            extract_just_name = extract_just_name + "_" + time_now

            if CAPTCHA_TYPE == "4":
                word_list_format.user_study_function(file_entry, study_output_folder, extract_just_name, audio_type,
                                                     gbl_rows, selected_rows)
            else:
                consecutive_words_format.user_study_function(file_entry, study_output_folder, extract_just_name,
                                                             audio_type, gbl_rows, selected_rows)

            logging.info("Done for : " + file_entry + " output : " + str(gbl_rows) + str(selected_rows))
            print("Done for : " + file_entry + " output : " + str(gbl_rows) + str(selected_rows))
            print(file_index)

            if len(gbl_rows) > 0:
                if global_csv_writer is None:
                    file_layout = open("logs\\detail_" + main_process_start_time + "_" + OUT_TAG + ".csv", "w",
                                       newline='')
                    global_csv_writer = csv.writer(file_layout)

                global_csv_writer.writerows(gbl_rows)
                gbl_rows = []
            if len(selected_rows) > 0:
                if selected_csv_writer is None:
                    selected_strings_layout = open("logs\\selected_" + main_process_start_time + "_" + OUT_TAG + ".csv",
                                                   "w", newline='')
                    selected_csv_writer = csv.writer(selected_strings_layout)
                selected_csv_writer.writerows(selected_rows)
                selected_rows = []

        except Exception as fileException:
            print(str(fileException) + "_" + str(file_index))
            logging.error(str(fileException))


if __name__ == '__main__':

    # Chunk input files. Required because 30 min files don't return.
    try:
        audio_property_list = [
            {"type": "podcast_lecture", "output": "podcast_lecture/", "input": "podcast_lecture/",
             "chunk_required": False},
            {"type": "YT_lecture", "output": "lecture/", "input": "lecture/", "chunk_required": True},
            {"type": "movie", "output": "movie/", "input": "movie/", "chunk_required": False},
            {"type": "song", "output": "song/", "input": "song/", "chunk_required": False},
            {"type": "radio", "output": "radio/", "input": "philip_marlowe/", "chunk_required": False}]

        for type_entry in audio_property_list:

            chunk_location = os.path.join(global_constants.INPUT_CHUNK_STAGE, type_entry["output"])
            try:
                os.makedirs(chunk_location)
            except OSError:
                pass

            if type_entry["chunk_required"]:

                if type_entry["type"] == "song":
                    func_lib.AUDIO_CHUNK_SIZE_SECONDS = 10

                original_no_chunk_data = type_entry["input"]
                file_name_list = glob.glob(global_constants.INPUT_DATA_STAGE + original_no_chunk_data + "*")

                func_lib.save_to_chunks(file_name_list, chunk_location, original_no_chunk_data)

            if type_entry['type'] != "podcast_lecture":
                continue

            # prepare_for_user_study(chunk_location, type_entry["type"], main_process_start_time, file_ending=".wav")

    except Exception as e:
        logging.error(str(e))

    print("Done")
