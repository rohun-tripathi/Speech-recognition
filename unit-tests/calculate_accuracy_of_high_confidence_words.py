import function_library
import pandas as pd
from glob import glob

file_list = glob("accuracy_plot_data/" + "*.wav")
file_list = sorted(file_list)

data_matrix = [["word", "confidence", "length", "characters"]]

for index, file_name in enumerate(file_list):

    if index > 10:
        break

    result = function_library.transcribe_robustly(file_name)

    result_dict = function_library.get_dict(result)
    transcription = function_library.get_dict(result, tag="alternatives")
    predicted_word_list = function_library.get_word_list(result_dict)

    for word_obj in predicted_word_list:
        data_matrix.append([word_obj.word, word_obj.confidence, word_obj.end_time - word_obj.start_time, word_obj.length])

data = pd.DataFrame(data_matrix)

data.to_excel("prediction_buckets_to_accuracy.xlsx")