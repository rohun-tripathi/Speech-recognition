import argparse
from datetime import datetime
from os.path import join

import global_constants as constant
import main
import function_library

import traceback

import logging

import os

arg_object = argparse.ArgumentParser()

arg_object.add_argument("-g", "--group", help="data in example sub folder path/name/tag", default="youtube_lecture")
arg_object.add_argument("-d", "--data", help="data folder path. Other folders are relative to this folder", default="reboot_rerun")
arg_object.add_argument("-i", "--input", help="input sub folder", default="input")
arg_object.add_argument("-c", "--chunk", help="chunk sub folder", default="chunk_folder")
arg_object.add_argument("-a", "--audioclippeddata", help="Clips sent to IBM server for review", default='other_audio')
arg_object.add_argument("-s", "--selected", help="Clips sent to IBM and selected for CAPTCHA", default='selected')
arg_object.add_argument("-p", "--produce_chunk", action='store_true', help='Produce chunks from the input data or not')

args = arg_object.parse_args()

if args.data is not None:
    constant.DATA_FOLDER = args.data

if args.input is not None:
    constant.INPUT_DATA_STAGE = join(constant.DATA_FOLDER, args.input)

if args.chunk is not None:
    constant.INPUT_CHUNK_STAGE = join(constant.DATA_FOLDER, args.chunk)

if args.selected is not None:
    constant.OUTPUT_DATA_SELECTED = join(constant.DATA_FOLDER, args.selected)

if args.audioclippeddata is not None:
    constant.OUTPUT_DATA_DETAILS_STAGE = join(constant.DATA_FOLDER, args.audioclippeddata)

print("Global contants set to : ")

print(args.group)
print("DATA_FOLDER", constant.DATA_FOLDER)
print("INPUT_DATA", constant.INPUT_DATA_STAGE)
print("INPUT_CHUNK", constant.INPUT_CHUNK_STAGE)
print("OUTPUT_DATA_SELECTED", constant.OUTPUT_DATA_SELECTED)
print("OUTPUT_DATA_DETAILS", constant.OUTPUT_DATA_DETAILS_STAGE)

for output_path in [constant.INPUT_CHUNK_STAGE, constant.OUTPUT_DATA_SELECTED, constant.OUTPUT_DATA_DETAILS_STAGE]:
    os.makedirs(output_path, exist_ok=True)

try:
    main_process_start_time = str(datetime.now()).replace(" ", "_").replace(":", "_").replace(".", "_")
    output_file_tag = "UNIT_TEST_" + constant.CAPTCHA_TYPE
    chunk_location = join(constant.INPUT_CHUNK_STAGE, args.group)

    if args.produce_chunk:
        print("Begin Generating Chunk of input Audio")
        logging.info("Begin Generating Chunk of input Audio")
        function_library.save_to_chunks(constant.INPUT_DATA_STAGE, chunk_location, args.group)
    else:
        logging.info("Not producing chunks of input Audio")

    logging.info("Begin Generating Audio reCAPTCHA")
    main.produce_clips_for_user_study(chunk_location, args.group, main_process_start_time, output_file_tag,
                                      constant.OUTPUT_DATA_DETAILS_STAGE)
    logging.info("Exiting")

except OSError as osE:
    print("Possibly an error related to folder creation. Please check the sub folder directory creation. " + str(osE))
    traceback.print_exc()

except Exception as uE:
    print("Unknown error. " + str(uE))
    traceback.print_exc()
