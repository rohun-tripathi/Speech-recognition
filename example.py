import argparse
from datetime import datetime
from os.path import join

import global_constants as constant
import main
import function_library

import traceback

arg_object = argparse.ArgumentParser()

arg_object.add_argument("-g", "--group", help="data in example sub folder path/name/tag")
arg_object.add_argument("-d", "--data", help="data folder path")
arg_object.add_argument("-i", "--input", help="input sub folder")
arg_object.add_argument("-c", "--chunk", help="chunk sub folder")
arg_object.add_argument("-s", "--selected", help="final selected CAPTCHA output")
arg_object.add_argument("-a", "--audioclippeddata", help="proposed clips for CAPTCHA selection")

args = arg_object.parse_args()

folder_group = args.group if args.group is not None else "example"

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

print("Values provided : ")

print(folder_group)
print(constant.DATA_FOLDER)
print(constant.INPUT_DATA_STAGE)
print(constant.INPUT_CHUNK_STAGE)
print(constant.OUTPUT_DATA_SELECTED)
print(constant.OUTPUT_DATA_DETAILS_STAGE)

try:
    main_process_start_time = str(datetime.now()).replace(" ", "_").replace(":", "_").replace(".", "_")
    output_file_tag = "UNIT_TEST_" + constant.CAPTCHA_TYPE

    chunk_location = join(constant.INPUT_CHUNK_STAGE, folder_group)
    function_library.save_to_chunks(constant.INPUT_DATA_STAGE, chunk_location, folder_group)

    main.prepare_for_user_study(chunk_location, folder_group, main_process_start_time, output_file_tag,
                                constant.OUTPUT_DATA_DETAILS_STAGE)
    print("Exiting")

except OSError as osE:
    print("Possibly an error related to folder creation. Please check the sub folder directory creation. " + str(osE))
    traceback.print_exc()

except Exception as uE:
    print("Unknown error. " + str(uE))
    traceback.print_exc()
