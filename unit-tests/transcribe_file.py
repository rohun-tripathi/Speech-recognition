import function_library

file_name = "test.wav"

result = function_library.transcribe_robustly(file_name, speakers=True)

result_dict = function_library.get_dict(result)
transcription = function_library.get_dict(result, tag="alternatives")
predicted_word_list = function_library.get_word_list(result_dict)

print(transcription)
