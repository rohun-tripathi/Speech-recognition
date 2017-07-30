import base64
import csv
import json

import speech_recognition as sr

# IBM Transcription won't work anymore as the authentication has expired. Needs to be updated as the other
# implementation  is much smaller and more maintainable.

try:  # attempt to use the Python 2 modules
    from urllib import urlencode
    from urllib2 import Request, urlopen, URLError, HTTPError
except ImportError:  # use the Python 3 modules
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError

TRANSCRIPTION_TYPE_LIST = ["SPHINX", "GOOGLE_OLD", "GOOGLE_CLOUD", "IBM"]

DATA_SAMPLES = [("broke.flac", "I think I broke something"), ("face.flac", "I got something on my face"),
                ("maggot.flac", "On your feet maggot")]

IBM_USERNAME = "5dfc5316-3ce3-4eb6-990f-af095739f349"  # form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
IBM_PASSWORD = "oLQpSIHfNwzp"  # passwords are mixed-case alphanumeric strings

GOOGLE_CLOUD_SPEECH_CREDENTIALS = """{
  "type": "service_account",
  "project_id": "fiery-aspect-162501",
  "private_key_id": "02c3770e740ffc969962e19bdbb7bfd473a24708",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC+ac+5foaaUt35\n3Jj6UxtfCzEBnMCz9M4mk+mL0y/wrbOynVgci8z60UG37eU/h9LIvDcXqB/YTtLN\nzySmfG+LpCh71bHoqRY0sUmNViJ2KBQQHIZKB0esX0P6CZVel+KLEDGWNBOz8ch9\n70SE2kng2DrppQWEWxLNbQdSOPf34baLIBVQ2AfyCiiMmsRz0Fbx4fvcMS1ynecr\n1PhS3n6KNAVPziXS63w7jcyDSHgfiTDDLbQ2BK1f83QdEg2RsxiB8rRZLNwTR9SN\n/+P3Y6VHPu6Yuku69bzIa7jKmlJFTaecrCqGxydD3MAt3mwyriOEn2eFjYFWYkep\nRqGl7477AgMBAAECggEAEdnZn4o9FDqwlLwZm14vMrnZ3kzTxAsvSG6VdoZV+DpQ\nnm4h1ItGrDzx7ExhMZOKL0d14sHgOmcpXCIPTYxc6Lp7ESD3jNhNPKNiQd3RXUJk\nnx4NeOM11PMZbFd5qWST2HWsMGixcC06npPP2KSeSHX9D+pomf/vw1J1XT/5/0MA\nRdzGsr8cyrHkAZpB9CFfZn5pdsnJasTyFOq4QNxNxgPBWm5cmqQdJUtSBZEgSrK5\nRox7Myrb0X37pxFXl/8iwCNLprefQmjZQiaOcvceTwtXnSUrE78qS2XflTeO2Yb0\nAkyvtRjUflHoQLRrF9DERV3OH2VrZn6z5kVqU0+AAQKBgQDydsDAq45pimDn5ED9\nvUtylrgSLOnq+1CnCxMQDfVkA01qj4CpW0l9fh0kTg3kfIUl1uH5fI6EwDetDZHO\nWcyRp2BO2oLJgNeB27pYpRYIwbJbPWfOJR+gvRqszty2CA5hmFEKhZ4wks+Z43sW\ngQt4aE+fCvfZstqFdvm3BYD6GQKBgQDJCyl5VQujVGH5LcGgx7a+sevqInnq8V63\nDOQGdA3Tw4D206XcF5pWWRZaK8Oqejk13rj9Z+AzcVM62aBNfvQUN6c9E9x9fMSA\n55zaQhI5mSWhq3TQjBOGRU9BhXFw3Fa1oakKmM3luh41g9wtLyQqMDmjQxqJzxv9\n/T7kQ1scMwKBgQDXqtWtC2wzaIjl+1vr11Ki7HlygUzYXQ7SZsFgCGp7uYxE+rwg\n6DgoTeMyBdPJpxDwJYD/X9GNN0TOw0EsYSfbbxv1R9wJzHbk5UON0doVk+VHzwjk\njpThbxOpHp+nsubH3KpJR6z727qZUYSM8d/4DCC2gRURKUvCZ5+bMmQVEQKBgAQc\nUlDEyGQiiY5KvTbIXpgvkx9KbSu8m68qeE8ZeF7oFG73jOCfKuyxDZ/yXSHTNfBA\nCZBE23Sx0H3XjUuIWP1A1g6NpWh7cJkiIzbjOvQqiXZwxwaslomcSS6Rx+wC1VMJ\nZydsUGluEMgPViUmXZrvOX55FMXUkkHzN6H7LpW5AoGAE4UmIFgeqs+y97/yxARG\nRVnD6DSwRH0PtZgNSX2WiYz8Z8CFGi1agteJKEZ6bmI9QsBdxJ53HH3MeAjWM7Mr\nlb+S+ViHyFVn09lb8hTraSa3+Mlg5iKk1TMmYnKQ4G/NrRp6IbfP19LAobXgBmQv\nBrgOpTiIHkcxTjplTdeS9kY=\n-----END PRIVATE KEY-----\n",
  "client_email": "272709675122-compute@developer.gserviceaccount.com",
  "client_id": "102127487461853832688",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/272709675122-compute%40developer.gserviceaccount.com"
}
"""


def extracted_from_sr_recognize_ibm(audio_data, username, password, language="en-US", show_all=False, timestamps=False,
                                    word_confidence=False):
    assert isinstance(username, str), "``username`` must be a string"
    assert isinstance(password, str), "``password`` must be a string"

    flac_data = audio_data.get_flac_data(
        convert_rate=None if audio_data.sample_rate >= 16000 else 16000,  # audio samples should be at least 16 kHz
        convert_width=None if audio_data.sample_width >= 2 else 2  # audio samples should be at least 16-bit
    )
    url = "https://stream-fra.watsonplatform.net/speech-to-text/api/v1/recognize?{}".format(urlencode({
        "profanity_filter": "false",
        "continuous": "true",
        "model": "{}_BroadbandModel".format(language),
        "timestamps": "{}".format(str(timestamps).lower()),
        "word_confidence": "{}".format(str(word_confidence).lower())
    }))
    request = Request(url, data=flac_data, headers={
        "Content-Type": "audio/x-flac",
        "X-Watson-Learning-Opt-Out": "true",  # prevent requests from being logged, for improved privacy
    })
    authorization_value = base64.standard_b64encode("{}:{}".format(username, password).encode("utf-8")).decode("utf-8")
    request.add_header("Authorization", "Basic {}".format(authorization_value))

    try:
        response = urlopen(request, timeout=None)
    except HTTPError as e:
        raise sr.RequestError("recognition request failed: {}".format(e.reason))
    except URLError as e:
        raise sr.RequestError("recognition connection failed: {}".format(e.reason))
    response_text = response.read().decode("utf-8")
    result = json.loads(response_text)

    # return results
    if show_all: return result
    if "results" not in result or len(result["results"]) < 1 or "alternatives" not in result["results"][0]:
        raise Exception("Unknown Value Exception")

    transcription = []
    for utterance in result["results"]:
        if "alternatives" not in utterance:
            raise Exception("Unknown Value Exception. No Alternatives returned")
        for hypothesis in utterance["alternatives"]:
            if "transcript" in hypothesis:
                transcription.append(hypothesis["transcript"])
    return "\n".join(transcription)


def get_transcription_result_by_type(audio, type, recognizer):
    try:
        if type == "SPHINX":
            transcribed_value = recognizer.recognize_sphinx(audio)
        elif type == "GOOGLE_OLD":
            transcribed_value = recognizer.recognize_google(audio)
        elif type == "GOOGLE_CLOUD":
            transcribed_value = recognizer.recognize_google_cloud(audio,
                                                                  credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
        elif type == "IBM":
            transcribed_value = extracted_from_sr_recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD)
        else:
            raise Exception("provided type not defined : {0}".format(type))

        return transcribed_value, True

    except sr.UnknownValueError:
        return "Could not understand audio", False
    except sr.RequestError as e:
        return "Sphinx error; {0}".format(e), False
    except Exception as e:
        return "Unknown error; {0}".format(e), False


def transcribe_audio_file(audio_file, ground_truth, transcription_type_list=TRANSCRIPTION_TYPE_LIST):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)

    correct_classifications = 0
    row_for_audio_instance = []
    for type in transcription_type_list:
        result, success_boolean = get_transcription_result_by_type(audio, type, recognizer)
        if success_boolean:
            successful_transcription = result.strip() == ground_truth
            row_for_audio_instance.extend([result, str(successful_transcription)])
            if successful_transcription: correct_classifications += 1
        else:
            row_for_audio_instance.extend([result, "Error"])

    return row_for_audio_instance, correct_classifications


def transcribe_types(sample_list=DATA_SAMPLES, transcription_type_list=TRANSCRIPTION_TYPE_LIST):
    header = ["File Name", "Ground Truth", "Correct Classifications"]
    for type in transcription_type_list:
        header.extend([type, type + "_result_match"])
    rows = [header]

    for sample_tuple in sample_list:
        row, total_correct = transcribe_audio_file(sample_tuple[0], sample_tuple[1], transcription_type_list)
        complete_row = [sample_tuple[0], sample_tuple[1], total_correct] + row
        rows.append(complete_row)

    transcription_result = open("transcription_result.csv", "w", newline='')
    csv_writer = csv.writer(transcription_result)
    csv_writer.writerows(rows)
    transcription_result.close()


def transcribe_using_ibm():
    file_name = "broke.flac"
    data_dump = open("data_output\\ibm_word_confidence_timestamp_dump.txt", "w")

    r = sr.Recognizer()
    with sr.AudioFile(file_name) as source:
        audio = r.record(source)

    try:
        result = extracted_from_sr_recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD, show_all=True,
                                                 word_confidence=True, timestamps=True)

        result = {} if result is None else result
        result["file_name"] = file_name
        data_dump.write(str(result))
    except sr.UnknownValueError:
        print("IBM Speech to Text could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from IBM Speech to Text service; {0}".format(e))
    except Exception as e:
        print(e)

    data_dump.close()


if __name__ == "__main__":
    sample_list = [("data_input\\hi.wav", "cju3j")]
    transcribe_types(sample_list, ["GOOGLE_CLOUD"])
