import csv
import glob
import re
import os
from random import Random

from datetime import datetime
import logging

import function_library as func_lib
import word_list_format
import consecutive_words_format

OUT_TAG = "REFACTORED" + "_" + func_lib.NOISE_TYPE + "_" + "YT" + "_VERSION_" + func_lib.VERSION_NUMBER


def prepare_for_user_study(user_study_input_data, audio_type, time_now, file_ending=".wav"):
    file_list = glob.glob(user_study_input_data + "*" + file_ending)
    Random(4).shuffle(file_list)

    length_portion = int(len(file_list) / 8)
    if func_lib.VERSION_NUMBER == "2":
        # file_list = file_list[0:length_portion]
        file_list = file_list[length_portion * 4: length_portion * 5]
    elif func_lib.VERSION_NUMBER == "3a":
        file_list = file_list[length_portion: length_portion * 2]
    elif func_lib.VERSION_NUMBER == "3b":
        file_list = file_list[length_portion * 7: length_portion * 8]
    #        file_list = file_list[length_portion * 6: length_portion * 7]
    #        file_list = file_list[length_portion * 2: length_portion * 3]
    elif func_lib.VERSION_NUMBER == "4":
        file_list = file_list[length_portion * 3: length_portion * 4]

    # Done All. More data if required
    file_list = file_list[:]

    gbl_rows = []
    selected_rows = []

    source_regex = r"(?<=" + re.escape(user_study_input_data) + r").+?(?=.wav)"

    # This can be improved
    study_output_folder = "user_study_output\\"

    break_execution = False
    for file_entry in file_list:
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

            if func_lib.VERSION_NUMBER == "4":
                word_list_format.user_study_function(file_entry, study_output_folder, extract_just_name, audio_type,
                                                     gbl_rows, selected_rows)
            else:
                consecutive_words_format.user_study_function(file_entry, study_output_folder, extract_just_name,
                                                             audio_type, gbl_rows, selected_rows)

            logging.info("Done for : " + file_entry + " output : " + str(gbl_rows) + str(selected_rows))
            print("Done for : " + file_entry + " output : " + str(gbl_rows) + str(selected_rows))

            if len(gbl_rows) > 0:
                global_csv_writer.writerows(gbl_rows)
                gbl_rows = []

            if len(selected_rows) > 0:
                selected_csv_writer.writerows(selected_rows)
                selected_rows = []

        except Exception as fileException:
            logging.error(str(fileException))


if __name__ == '__main__':

    now = str(datetime.now().timestamp()).replace(".", "")

    # Logging
    file_layout = open("logs\\detail_" + now + "_" + OUT_TAG + ".csv", "w", newline='')
    global_csv_writer = csv.writer(file_layout)

    selected_strings_layout = open("logs\\selected_" + now + "_" + OUT_TAG + ".csv", "w", newline='')
    selected_csv_writer = csv.writer(selected_strings_layout)

    logging.basicConfig(filename='process_logs\\info_' + func_lib.VERSION_NUMBER + '.log', format='%(message)s',
                        level=logging.INFO)

    # Chunk input files. Required because 30 min files don't return.
    try:
        base_output_folder = "user_study_output\\user_study_initial_output\\"
        audio_property_list = [
            {"type": "podcast_lecture", "output": "podcast_lecture\\", "input": "podcast_lecture\\",
             "chunk_required": True},
            {"type": "YTlecture", "output": "lecture\\", "input": "lecture\\", "chunk_required": False},
            {"type": "movie", "output": "movie\\", "input": "movie\\", "chunk_required": False},
            {"type": "song", "output": "song\\", "input": "song\\", "chunk_required": False},
            {"type": "radio", "output": "radio\\", "input": "philip_marlowe\\", "chunk_required": False}]

        for type_entry in audio_property_list:

            # Focus on YT Lecture
            if type_entry['type'] != "podcast_lecture":
                continue

            chunk_location = base_output_folder + type_entry["output"]
            os.makedirs(chunk_location, exist_ok=True)

            if type_entry["chunk_required"]:

                if type_entry["type"] == "song":
                    func_lib.AUDIO_CHUNK_SIZE_SECONDS = 10

                original_no_chunk_data = type_entry["input"]
                file_name_list = glob.glob("data_input\\" + original_no_chunk_data + "*")

                func_lib.save_to_chunks(file_name_list, chunk_location, original_no_chunk_data)

            prepare_for_user_study(chunk_location, type_entry["type"], now, file_ending=".wav")

    except Exception as e:
        logging.error(str(e))

    file_layout.close()
    selected_strings_layout.close()

    print("Done")
