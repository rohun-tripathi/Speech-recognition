import os

import global_constants
import main
import function_library as func_lib

IGNORE_START_WORDS = 6
TIME_BEFORE_FIRST_WORD = 2.0
TIME_AFTER_SECOND_WORD = 1.0


def get_audio_segment():
    return func_lib.AudioSegment


def export_audio_patterns(initial_audio, first_word_audio, second_word_audio, final_audio, noisy_audio, noise,
                          required_out_file_name, silence):
    complete_file_name = os.path.join(global_constants.OUTPUT_DATA_SELECTED, required_out_file_name + ".wav")
    noisy_audio.export(out_f=complete_file_name, format="wav")

    # beep = get_audio_segment().from_file("parameter_input\\beep_2.wav", format="wav")
    # long_silence = get_audio_segment().silent(duration=400)

    # noisy_audio = get_noisy_beep_audio(beep, final_audio, first_word_audio, initial_audio, long_silence, noise,
    #                                    second_word_audio, silence)
    # beep_file_name = os.path.join(OUTPUT_DATA_SELECTED, required_out_file_name + "_W_B.wav")
    # noisy_audio.export(beep_file_name, format="wav")
    #
    # noisy_audio = long_silence.overlay(noise, loop=True) + first_word_audio.overlay(noise, loop=True) + \
    #               second_word_audio.overlay(noise, loop=True) + long_silence.overlay(noise, loop=True)
    # beep_file_name = os.path.join(OUTPUT_DATA_SELECTED, required_out_file_name + "_O_B.wav")
    # noisy_audio.export(beep_file_name, format="wav")


def get_noisy_beep_audio(beep, final_audio, first_word_audio, initial_audio, long_silence, noise, second_word_audio,
                         silence):
    if func_lib.NOISE_THROUGH_OUT:
        noisy_audio = silence + initial_audio.overlay(noise, loop=True) + silence.overlay(noise,
                                                                                          loop=True) + beep + long_silence.overlay(
            noise, loop=True) + \
                      first_word_audio.overlay(noise, loop=True) + second_word_audio.overlay(noise, loop=True) + \
                      long_silence.overlay(noise, loop=True) + beep + silence.overlay(noise,
                                                                                      loop=True) + final_audio.overlay(
            noise, loop=True) + silence
    else:
        noisy_audio = silence + initial_audio + silence + beep + long_silence.overlay(noise, loop=True) + \
                      first_word_audio.overlay(noise, loop=True) + second_word_audio.overlay(noise, loop=True) + \
                      long_silence.overlay(noise, loop=True) + beep + silence + final_audio + silence
    return noisy_audio


def call_for_different_word_length(audio, initial_objects, first_object, second_object, final_objects, noise,
                                   noise_type, required_out_file_name, user_study_output, row, first_easy):
    silence = get_audio_segment().silent(duration=250)
    output_file_name = os.path.join(user_study_output, required_out_file_name + ".wav")

    first_word_start = first_object.start_time
    second_word_start = second_object.start_time

    if len(initial_objects) == 0:
        audio_start_time = first_word_start
    else:
        audio_start_time = initial_objects[0].start_time

    final_start_time = second_object.end_time
    if len(final_objects) == 0:
        final_end_time = final_start_time
    else:
        final_end_time = final_objects[-1].end_time

    initial_audio = audio[audio_start_time * 1000:first_word_start * 1000]
    first_word_audio = audio[first_word_start * 1000:second_word_start * 1000]
    second_word_audio = audio[second_word_start * 1000:final_start_time * 1000]
    final_audio = audio[final_start_time * 1000:final_end_time * 1000]

    noisy_audio = overlay_noise(final_audio, first_word_audio, initial_audio, noise, second_word_audio, silence)
    noisy_audio.export(output_file_name, format="wav")

    result = func_lib.transcribe_robustly(output_file_name)
    result_dict = func_lib.get_dict(result)
    word_list = func_lib.get_word_list(result_dict)
    transcription = func_lib.get_dict(result, tag="alternatives")

    row.extend([noise_type, first_object.word, second_object.word, str(transcription)])
    for word_object in word_list:
        row.extend([word_object.word, word_object.confidence])

    print("Transcription : " + str(transcription) + "\nResultant Prediction : " + str(result_dict) + "\n")

    audio_start_offset = audio_start_time - len(silence) / 1000

    stt_confident_object = first_object if first_easy else second_object
    # As soon as we find the first lowered word, we return.
    _, is_lowered_sufficiently = \
        func_lib.check_word_confidence(word_list, [stt_confident_object], audio_start_offset)

    if is_lowered_sufficiently:
        export_audio_patterns(initial_audio, first_word_audio, second_word_audio, final_audio, noisy_audio, noise,
                              required_out_file_name, silence)

    return is_lowered_sufficiently, row


def overlay_noise(final_audio, first_word_audio, initial_audio, noise, second_word_audio, silence):
    if func_lib.NOISE_THROUGH_OUT:
        noisy_audio = silence + initial_audio.overlay(noise, loop=True) + first_word_audio.overlay(noise, loop=True) + \
                      second_word_audio.overlay(noise, loop=True) + final_audio.overlay(noise, loop=True) + silence
    else:
        noisy_audio = silence + initial_audio + first_word_audio.overlay(noise, loop=True) + \
                      second_word_audio.overlay(noise, loop=True) + final_audio + silence
    return noisy_audio


# noinspection PyPep8Naming
def add_noise_experiment(initial_objects, first_object, second_object, final_objects, first_easy, audio_clip,
                         output_location, required_out_file_name, audio_type, gbl_rows, selected_rows):
    original_word_list = initial_objects[:] + [first_object, second_object] + final_objects
    high_level_transcription, start_time, end_time = func_lib.merge_transcription_from_parts(original_word_list)

    noise_type, input_noise = func_lib.get_noise()

    # The threshold value we are working with is 0.8 * original power. Now 10 * log(0.8) ~ -1
    maximum_allowed_dBFS = audio_clip.dBFS - 1

    step_size = 10
    noise_to_add = -1
    best_solution = None

    if input_noise.dBFS > maximum_allowed_dBFS:
        return

    while step_size >= 1:

        # Initial No Noise
        if noise_to_add == -1:
            noise = get_audio_segment().silent(duration=250)

        else:
            noise = input_noise + noise_to_add

            if noise.dBFS > maximum_allowed_dBFS:
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
        row = [iteration_out_file_name, global_constants.CAPTCHA_TYPE, start_time, end_time, high_level_transcription, noise_to_add, first_easy,
               first_object.confidence, second_object.confidence, audio_type]

        found_unique, row = call_for_different_word_length(audio_clip, initial_objects, first_object, second_object,
                                                           final_objects, noise, noise_type, iteration_out_file_name,
                                                           output_location, row, first_easy)
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


def user_study_function(file_name, user_study_output, extracted_out_put_filename, audio_type, gbl_rows, selected_rows):
    result = func_lib.transcribe_robustly(file_name, True)

    result_dict = func_lib.get_dict(result)
    res_start_time, res_end_time, res_confidence, res_word = func_lib.get_res_details(result_dict)
    word_object_list = func_lib.get_word_list(result_dict)
    speaker_list = func_lib.get_speaker_list(result)

    word_index = IGNORE_START_WORDS
    count = 0

    while word_index < len(res_end_time) - 1:
        # Check if the two consecutive words have high and low confidence and vice versa
        if (res_confidence[word_index] > global_constants.HIGH_CONF_THRESHOLD and res_confidence[
                word_index - 1] < global_constants.LOW_CONF_THRESHOLD) or \
                (res_confidence[word_index - 1] > global_constants.HIGH_CONF_THRESHOLD and res_confidence[
                    word_index] < global_constants.LOW_CONF_THRESHOLD):

            if len(res_word[word_index]) < func_lib.MINIMUM_NUMBER_OF_CHAR or \
                            len(res_word[word_index - 1]) < func_lib.MINIMUM_NUMBER_OF_CHAR:
                print("Skipped words because one is less than minimum no_of_char_per_word: " +
                      str(res_word[word_index - 1]) + " " + str(res_word[word_index]))
                word_index += 1
                continue

            if (len(res_word[word_index]) < func_lib.MINIMUM_NUMBER_OF_CHAR + 1 and
                        len(res_word[word_index - 1]) < func_lib.MINIMUM_NUMBER_OF_CHAR + 1):
                print("Skipped words because both are less than no_of_char_per_word + 1 chars: " +
                      str(res_word[word_index - 1]) + " " + str(res_word[word_index]))
                word_index += 1
                continue

            first_word_object = word_object_list[word_index - 1]
            second_word_object = word_object_list[word_index]

            if not func_lib.is_word_set_eligible([first_word_object, second_word_object]):
                print("Skipped words because word set not eligible")
                word_index += 1
                continue

            if not func_lib.is_length_within_limits([first_word_object, second_word_object]):
                print("Skipped words because word length is not within limits")
                word_index += 1
                continue

            first_easy = res_confidence[word_index - 1] > res_confidence[word_index]
            move_to_value = word_index

            # Initial value at set at clip start
            transcription_start_index = 0

            # Initial value at set at clip end
            transcription_end_index = -1

            if func_lib.USE_ONLY_TWO_WORDS:
                audio_start_time = res_start_time[word_index - 1]
                transcription_start_index = word_index - 1
            else:
                audio_start_time = res_start_time[word_index - 1] - TIME_BEFORE_FIRST_WORD

            if audio_start_time < 0:
                audio_start_time = 0
                transcription_start_index = 0

            if func_lib.USE_LAST_TWO_WORD or func_lib.USE_ONLY_TWO_WORDS:
                audio_end_time = res_end_time[word_index]
                transcription_end_index = word_index
            else:
                audio_end_time = res_end_time[word_index] + TIME_AFTER_SECOND_WORD

            # If end time exceeds clip end, set to the time of clip end.
            if audio_end_time >= res_end_time[len(res_end_time) - 1]:
                audio_end_time = res_end_time[len(res_end_time) - 1]
                transcription_end_index = len(res_end_time) - 1

            # Make sure that the start and end time is not between a word
            for j in range(0, len(res_end_time) - 1):
                if res_start_time[j] >= audio_start_time:
                    transcription_start_index = j
                    break

            for j in range(0, len(res_end_time)):
                if res_end_time[j] >= audio_end_time:
                    # There is an possible issue here. Checked it later by checking that the len of final objects > 1
                    transcription_end_index = j
                    move_to_value = j - 1
                    break

            initial_objects = word_object_list[transcription_start_index:word_index - 1]
            final_word_objects = word_object_list[word_index + 1:transcription_end_index + 1]

            joined_word_list = initial_objects + [first_word_object, second_word_object] + final_word_objects
            if not func_lib.is_length_within_limits(joined_word_list):
                print("Skipped words because word length is not within limits")
                word_index += 1
                continue

            if (not func_lib.USE_LAST_TWO_WORD and len(initial_objects) == 0) or (
                        not (func_lib.USE_LAST_TWO_WORD or func_lib.USE_ONLY_TWO_WORDS) and len(final_word_objects) == 0):
                print("Skipped words because either initial or final words are empty: " + str(initial_objects)
                      + str(final_word_objects))
                word_index += 1
                continue

            # If there are more than one speakers, this clip is not considered.
            if not func_lib.is_speaker_unique(speaker_list, word_object_list[transcription_start_index].start_time,
                                              word_object_list[transcription_end_index + 1].end_time):
                print("Skipped words because number of speakers over limit")
                word_index += 1
                continue

            format_index = file_name.rfind(".")  # find the last occurrence of dot
            audio = get_audio_segment().from_file(file_name, file_name[format_index + 1:])

            add_noise_experiment(initial_objects, first_word_object, second_word_object, final_word_objects, first_easy,
                                 audio, user_study_output, extracted_out_put_filename + "_count_" + str(count),
                                 audio_type, gbl_rows, selected_rows)

            word_index = move_to_value if move_to_value > word_index + 4 else word_index + 4
            count += 1

        word_index += 1
