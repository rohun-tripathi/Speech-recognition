CAPTCHA_TYPE = "3b"

PROJECT_FOLDER = "/Users/rohuntripathi/speech-recognition/"

DATA_FOLDER = PROJECT_FOLDER + "audio_data/"

OUTPUT_DATA_DETAILS_STAGE = DATA_FOLDER + "data_output_details_stage/"
OUTPUT_DATA_SELECTED = DATA_FOLDER + "data_output_selected/"
INPUT_CHUNK_STAGE = DATA_FOLDER + "data_chunk_stage/"
INPUT_DATA_STAGE = DATA_FOLDER + "data_input_stage/"

# IBM Watson STT Service Credentials
IBM_PASSWORD = 'PzYkToN7MahK'
IBM_USERNAME = '5fcf88bb-0112-46b5-9a0a-d5fef9399fb7'

NOISE_TYPE = "White"

AUDIO_CHUNK_SIZE_SECONDS = 25
MIN_AUDIO_CHUNK_SIZE_SECONDS = 5

HIGH_CONF_THRESHOLD = 0.70
LOW_CONF_THRESHOLD = 0.5

# Threshold for Audio Loudness. Clips louder than this threshold are clipped to this value.
AUDIO_LOUDNESS_THRESHOLD = -11.44
