CAPTCHA_TYPE = "3b"

PROJECT_FOLDER = "../speech-recognition/"

DATA_FOLDER = "audio_data/"

OUTPUT_DATA_DETAILS_STAGE = DATA_FOLDER + "output_details_stage/"
OUTPUT_DATA_SELECTED = DATA_FOLDER + "output_selected/"
INPUT_CHUNK_STAGE = DATA_FOLDER + "chunk_stage/"
INPUT_DATA_STAGE = DATA_FOLDER + "input_stage/"

# IBM Watson STT Service Credentials
IBM_PASSWORD = 'jCSY7Grqq8fY'
IBM_USERNAME = 'a9cf72e5-e5ba-482c-9477-0ca60a5edee7'

NOISE_TYPE = "White"

AUDIO_CHUNK_SIZE_SECONDS = 25
MIN_AUDIO_CHUNK_SIZE_SECONDS = 5

HIGH_CONF_THRESHOLD = 0.70
LOW_CONF_THRESHOLD = 0.5

# Threshold for Audio Loudness. Clips louder than this threshold are clipped to this value.
AUDIO_LOUDNESS_THRESHOLD = -11.44
