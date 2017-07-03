import os

import audio_v5
import function_library as func_lib

# Clip Properties ##############################################

IGNORE_START_WORDS = 2

PHRASE_WORD_LENGTH = 7
INCREMENT_WORD_LENGTH = 4


def get_audio_segment():
    return func_lib.AudioSegment


def test_stt_ability(audio, original_word_list, noise,
                     noise_type, required_out_file_name, user_study_output, row):
    silence = get_audio_segment().silent(duration=250)
    output_file_name = os.path.join(user_study_output, required_out_file_name + ".wav")

    audio_start_time = original_word_list[0].start_time
    audio_end_time = original_word_list[-1].end_time

    initial_audio = audio[audio_start_time * 1000:audio_end_time * 1000]

    noisy_audio = silence + initial_audio.overlay(noise, loop=True) + silence
    noisy_audio.export(output_file_name, format="wav")

    result = func_lib.transcribe_robustly(output_file_name)
    result_dict = func_lib.get_dict(result)
    predicted_word_list = func_lib.get_word_list(result_dict)
    transcription = func_lib.get_dict(result, tag="alternatives")

    row.extend([noise_type, str(transcription)])

    audio_start_offset = audio_start_time - len(silence) / 1000

    # If we find first appropriate, then pack up.
    reduced_word, is_lowered_sufficiently = \
        func_lib.check_word_confidence(predicted_word_list, original_word_list, audio_start_offset)
    if is_lowered_sufficiently:
        row.append(reduced_word)
        complete_file_name = os.path.join("user_study_output\\reduced_confidence\\", required_out_file_name + ".wav")
        noisy_audio.export(out_f=complete_file_name, format="wav")

    else:
        row.append("")

    for word_object in predicted_word_list:
        row.extend([word_object.word, word_object.confidence])

    return is_lowered_sufficiently, row


# noinspection PyPep8Naming
def increase_noise(word_list, audio_clip, output_location, required_out_file_name, audio_type, gbl_rows, selected_rows):
    high_level_transcription, start_time, end_time = func_lib.merge_transcription_from_parts(word_list)

    noise_type, input_noise = func_lib.get_noise()

    # The threshold value we are working with is 0.8 * original power. Now 10 * log(0.8) ~ -1
    original_dBFS = audio_clip.dBFS - 1

    step_size = 10
    noise_to_add = -1
    best_solution = None

    if input_noise.dBFS > original_dBFS:
        return

    while step_size >= 1:

        # Initial No Noise
        if noise_to_add == -1:
            noise = get_audio_segment().silent(duration=250)

        else:
            noise = input_noise + noise_to_add

            if noise.dBFS > original_dBFS:
                reduced_step_size = int(step_size / 2)
                noise_to_add = noise_to_add - step_size + reduced_step_size
                step_size = reduced_step_size
                continue

            # Check if instance is worse than best solution
            if best_solution is not None and noise_to_add >= best_solution["noise_level"]:
                reduced_step_size = int(step_size / 2)
                noise_to_add = noise_to_add - step_size + reduced_step_size
                step_size = reduced_step_size
                continue

        iteration_out_file_name = required_out_file_name + "_noise_" + str(noise_to_add) + "_noise_type_" + noise_type
        row = [iteration_out_file_name, audio_v5.CAPTCHA_TYPE, high_level_transcription, noise_to_add,
               "; ".join(str(dummy_word) for dummy_word in word_list), audio_type]

        found_unique, row = test_stt_ability(audio_clip, word_list, noise, noise_type,
                                             iteration_out_file_name, output_location, row)
        gbl_rows.append(row[:])

        if not found_unique:

            if noise_to_add == -1:
                noise_to_add = 0

            else:
                noise_to_add += step_size
            continue

        # update best solution
        if best_solution is None or noise_to_add < best_solution["noise_level"]:
            best_solution = {"row": row[:], "noise_level": noise_to_add}
        else:
            # How do we ever get here?
            break

        if noise_to_add != 0 and noise_to_add != -1:
            reduced_step_size = int(step_size / 2)
            noise_to_add = noise_to_add - step_size + reduced_step_size
            step_size = reduced_step_size
            continue
        else:
            # Best Solution found with zero or minimal noise
            break

    if best_solution is not None:
        selected_rows.append(best_solution["row"])


# This should be improved.
# VarParam
def increment_phrase_index(phrase_index):
    return phrase_index + INCREMENT_WORD_LENGTH


def user_study_function(file_name, user_study_output, extracted_out_put_filename, audio_type, gbl_rows, selected_rows):
    result = func_lib.transcribe_robustly(file_name, True)

    speaker_list = func_lib.get_speaker_list(result)
    result_dict = func_lib.get_dict(result)
    word_object_list = func_lib.get_word_list(result_dict)

    phrase_index = IGNORE_START_WORDS

    file_part_count = 0
    while phrase_index + PHRASE_WORD_LENGTH < len(word_object_list) - 1:

        # Check if any have high and any have low confidence.

        high_confidence_words_exist = False
        low_confidence_words_exist = False
        words_in_window = word_object_list[phrase_index: phrase_index + PHRASE_WORD_LENGTH]

        if not func_lib.is_length_within_limits(words_in_window):
            print("Skipped words because word length is not within limits")
            phrase_index = increment_phrase_index(phrase_index)
            continue

        if not func_lib.is_word_set_eligible(words_in_window):
            print("Skipped words because word set not eligible")
            phrase_index = increment_phrase_index(phrase_index)
            continue

        if not func_lib.is_speaker_unique(speaker_list, words_in_window[0].start_time, words_in_window[-1].end_time):
            print("Skipped words because number of speakers over limit")
            phrase_index = increment_phrase_index(phrase_index)
            continue

        # VarParam To leave out words at the start and end of clip.
        words_to_leave_at_start_and_end = 1
        cropped_list = words_in_window[words_to_leave_at_start_and_end: -words_to_leave_at_start_and_end];

        for word in cropped_list:
            if word.length >= func_lib.MINIMUM_NUMBER_OF_CHAR:
                if word.confidence > func_lib.HIGH_CONF_THRESHOLD:
                    high_confidence_words_exist = True

                if word.confidence < func_lib.LOW_CONF_THRESHOLD:
                    low_confidence_words_exist = True

        if not (high_confidence_words_exist and low_confidence_words_exist):
            print("Skipped words because all above threshold are less than no_of_char_per_word.")
            phrase_index = increment_phrase_index(phrase_index)
            continue

        audio = get_audio_segment().from_file(file_name, "wav")

        file_part_name = extracted_out_put_filename + "_count_" + str(file_part_count)
        increase_noise(words_in_window, audio, user_study_output, file_part_name, audio_type, gbl_rows, selected_rows)

        phrase_index = increment_phrase_index(phrase_index)
        file_part_count += 1
