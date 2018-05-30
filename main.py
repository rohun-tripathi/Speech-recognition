import csv
import glob
import logging
import os
import re
from datetime import datetime
from random import Random

import global_constants
import function_library as func_lib

import consecutive_words_format
import word_list_format

# Logging
logs_folder = 'logs'
os.makedirs(logs_folder, exist_ok=True)

# Attempt to make the basic config instantiation global.
process_logs_folder = 'process_logs'
os.makedirs(process_logs_folder, exist_ok=True)

logging.basicConfig(filename=os.path.join(process_logs_folder, 'info_' + global_constants.CAPTCHA_TYPE + '.log'), format='%(message)s',
                    level=logging.INFO)


def prepare_for_user_study(study_input_folder, audio_type, process_time, output_file_tag, study_output_folder,
                           file_ending=".wav", global_csv_writer=None, selected_csv_writer=None):
    """Read the files
    Allocate to different Captcha Types
    Execute CAPTCHA generation for each file
    log eligible CAPTCHA files
    """

    file_list = glob.glob(study_input_folder + os.path.sep + "*" + file_ending)

    Random(4).shuffle(file_list)

    length_portion = int(len(file_list) / 3)

    if global_constants.CAPTCHA_TYPE == "2":
        file_list = file_list[length_portion * 0: length_portion * 1]
    elif global_constants.CAPTCHA_TYPE == "3b":
        file_list = file_list[length_portion * 1: length_portion * 2]
    elif global_constants.CAPTCHA_TYPE == "4":
        file_list = file_list[length_portion * 2: length_portion * 3]
    elif global_constants.CAPTCHA_TYPE == "3a":
        raise Exception("3a not generated anymore")
    else:
        raise Exception("Captcha Type not supported")

    gbl_rows = []
    selected_rows = []

    source_regex = r"(?<=" + re.escape(study_input_folder) + r").+?(?=.wav)"

    for file_index, file_entry in enumerate(file_list):
        try:
            func_lib.check_and_clip_loud_volume(file_entry)

            extract_just_name = re.findall(source_regex, file_entry)
            if len(extract_just_name) != 0:
                extract_just_name = extract_just_name[0]
            else:
                continue
            extract_just_name = extract_just_name + "_" + process_time

            if global_constants.CAPTCHA_TYPE == "4":
                word_list_format.user_study_function(file_entry, study_output_folder, extract_just_name, audio_type,
                                                     gbl_rows, selected_rows)
            else:
                consecutive_words_format.user_study_function(file_entry, study_output_folder, extract_just_name,
                                                             audio_type, gbl_rows, selected_rows)

            logging.info("Done for : " + file_entry + " output : " + str(gbl_rows) + str(selected_rows))

            if len(gbl_rows) > 0:

                # Lazy load because the system other wise creates loads of empty excel files for test procedures.
                if global_csv_writer is None:
                    file_layout = open(os.path.join("logs", "detail_" + process_time + "_" +
                                                    output_file_tag + ".csv"), "w", newline='')
                    global_csv_writer = csv.writer(file_layout)

                global_csv_writer.writerows(gbl_rows)
                gbl_rows = []
            if len(selected_rows) > 0:

                # Lazy load because the system other wise creates loads of empty excel files for test procedures.
                if selected_csv_writer is None:
                    selected_strings_layout = open(os.path.join("logs", "selected_" + process_time + "_" +
                                                                output_file_tag + ".csv"), "w", newline='')
                    selected_csv_writer = csv.writer(selected_strings_layout)
                selected_csv_writer.writerows(selected_rows)
                selected_rows = []

        except Exception as fileException:
            logging.error(str(fileException))


def main():
    """Chunk input files. Required because 30 min files don't return.
    The execute prepare_for_user_study for each audio source type.

    """
    try:
        audio_property_list = [
            {"type": "indian_lecture", "output": "indian_lecture/", "input": "indian_lecture/",
             "chunk_required": False},
            {"type": "podcast_lecture", "output": "podcast_lecture/", "input": "podcast_lecture/",
             "chunk_required": False},
            {"type": "YT_lecture", "output": "lecture/", "input": "lecture/", "chunk_required": False},
            {"type": "movie", "output": "movie/", "input": "movie/", "chunk_required": False},
            {"type": "song", "output": "song/", "input": "song/", "chunk_required": False},
            {"type": "radio", "output": "radio/", "input": "philip_marlowe/", "chunk_required": False}]

        for type_entry in audio_property_list:

            if type_entry['type'] != 'YT_lecture':
                continue

            chunk_location = os.path.join(global_constants.INPUT_CHUNK_STAGE, type_entry["output"])
            if type_entry["chunk_required"]:
                func_lib.save_to_chunks(global_constants.INPUT_DATA_STAGE, chunk_location, type_entry["input"])

            main_process_start_time = str(datetime.now()).replace(" ", "_").replace(":", "_").replace(".", "_")
            output_file_tag = "_".join(["REBOOT", type_entry['type'], global_constants.CAPTCHA_TYPE])

            prepare_for_user_study(chunk_location, type_entry["type"], main_process_start_time, output_file_tag, global_constants.OUTPUT_DATA_DETAILS_STAGE,
                                   file_ending=".wav")

    except Exception as e:
        logging.error(str(e))
        print(str(e))


if __name__ == '__main__':
    main()
