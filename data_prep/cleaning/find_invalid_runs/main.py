import numpy as np
import pandas as pd

from data_prep.cleaning.find_invalid_runs.choice import filter_hit_ratio
from data_prep.cleaning.find_invalid_runs.both_tasks import filter_runs_no_instruction, \
    filter_full_but_no_et_data, filter_runs_low_fps, \
    filter_wrong_glasses
from data_prep.cleaning.find_invalid_runs.choice import filter_runs_not_us, filter_runs_precision, filter_runs_offset, \
    filter_biased_choices, filter_bad_log_k
from data_prep.cleaning.find_invalid_runs.fix import runs_with_incomplete_fix_tasks, filter_runs_bad_time_measure, \
    missing_glasses
from utils.save_data import write_csv


def invalid_runs_global(data_trial, data_et, data_subject):
    print(f"""Clean runs that are otherwise not valid: """)

    # Not enough trials
    subjects_full_trial = data_trial \
        .loc[data_trial['trial_type_new'] == 'end', 'run_id'] \
        .unique()
    print(f'n={len(subjects_full_trial)} runs with full trials. ')

    subjects_not_full_trial = np.setdiff1d(
        data_trial['run_id'].unique(),
        subjects_full_trial)

    runs_not_follow_instructions = filter_runs_no_instruction(
        data_subject)
    runs_full_but_not_enough_et = \
        filter_full_but_no_et_data(data_et, data_trial)
    runs_low_fps = filter_runs_low_fps(data_trial, data_et, 3)
    runs_cannot_see = filter_wrong_glasses(data_subject)

    # Plotting saccades from the fix task showed no variance
    runs_no_saccade = [144, 171, 380]

    invalid_runs = list(
        set(subjects_not_full_trial) |
        set(runs_not_follow_instructions) |
        set(runs_low_fps) |
        set(runs_cannot_see) |
        set(runs_no_saccade) |
        set(runs_full_but_not_enough_et)
    )

    n_runs = len(data_trial['run_id'].unique())

    summary = pd.DataFrame({
        'name': [
            'subjects_not_full_trial',
            'runs_noInstruction',
            'runs_lowFPS',
            'runs_cannotSee',
            'runs_no_saccade',
            'runs_full_but_not_enough_et',
            'total'],
        'length': [
            len(subjects_not_full_trial),
            len(runs_not_follow_instructions),
            len(runs_low_fps),
            len(runs_cannot_see),
            len(runs_no_saccade),
            len(runs_full_but_not_enough_et),
            len(invalid_runs)],
        'percent': [
            len(subjects_not_full_trial) / n_runs,
            len(runs_not_follow_instructions) / n_runs,
            len(runs_low_fps) / n_runs,
            len(runs_cannot_see) / n_runs,
            len(runs_no_saccade) / n_runs,
            len(runs_full_but_not_enough_et) / n_runs,
            len(invalid_runs) / n_runs]
        })

    print(f"""\n n={n_runs} runs in total. Invalid_runs: \n"""
          f"""{round(summary, 2)}""")

    write_csv(summary,
              'global_invalid_runs.csv',
              'results', 'tables')

    return invalid_runs


def invalid_runs_choice(data_trial, data_et, data_subject):
    filter_runs_not_us(data_subject)

    runs_low_fps = filter_runs_low_fps(data_trial, data_et, 5)
    runs_low_precision = filter_runs_precision(data_subject, max_precision=0.15)
    runs_high_offset = filter_runs_offset(data_subject, max_offset=0.5)

    runs_low_hit_ratio = filter_hit_ratio(data_subject, min_hit_ratio=0.8)

    runs_bad_quality = list(
        set(runs_low_fps) |
        set(runs_low_precision) |
        set(runs_high_offset) |
        set(runs_low_hit_ratio))
    print(f"""n={len(runs_bad_quality)} runs had bad data quality \n""")

    # These runs have barely have any variation in gaze points
    runs_no_variance = np.intersect1d(
        data_subject['run_id'].unique(),
        [12, 23, 93, 144, 243, 258, 268, 343, 356, 373, 384, 386, 387,
         393, 404, 379, 410, 411, 417, 410, 417, 425, 429, 440, 441, 445,
         449, 458, 462, 475, 425, 488, 493])

    runs_biased_choices = filter_biased_choices(
        data_subject, data_trial,
        min_percentage=0.01, max_percentage=0.99)

    runs_missing_log_k, runs_noisy_log_k, runs_pos_log_k = \
        filter_bad_log_k(data_subject, max_noise=40)

    invalid_runs = list(

        set(runs_no_variance) |
        set(runs_biased_choices) |
        set(runs_missing_log_k) |
        set(runs_noisy_log_k) |
        set(runs_pos_log_k) |
        set(runs_low_fps) |
        set(runs_low_precision) |
        set(runs_high_offset) |
        set(runs_low_hit_ratio))

    n_runs = len(data_trial['run_id'].unique())

    summary_output = pd.DataFrame({
        'name': [
            'run nr. 144',
            'runs_biasedChoices',
            'runs_missingLogK',
            'runs_noisy_logK',
            'runs_pos_logK',
            'subjects_lowFPS',
            'runs_low_precision',
            'runs_high_offset',
            'runs_low_hit_ratio',
            'total'],
        'length': [
            len(runs_no_variance),
            len(runs_biased_choices),
            len(runs_missing_log_k),
            len(runs_noisy_log_k),
            len(runs_pos_log_k),
            len(runs_low_fps),
            len(runs_low_precision),
            len(runs_high_offset),
            len(runs_low_hit_ratio),
            len(invalid_runs)],
        'percent': [
            len(runs_no_variance) / n_runs,
            len(runs_biased_choices) / n_runs,
            len(runs_missing_log_k) / n_runs,
            len(runs_noisy_log_k) / n_runs,
            len(runs_pos_log_k) / n_runs,
            len(runs_low_fps) / n_runs,
            len(runs_low_precision) / n_runs,
            len(runs_high_offset) / n_runs,
            len(runs_low_hit_ratio) / n_runs,
            len(invalid_runs) / n_runs]
    })

    print(f"""n={n_runs} runs in total. Invalid runs for choice task: \n"""
          f"""{round(summary_output, 2)} \n""")

    return invalid_runs


def invalid_runs_fix(data_trial_fix, data_subject):
    runs_incomplete_fix_task = runs_with_incomplete_fix_tasks(
        data_trial_fix)
    runs_bad_time_measure = filter_runs_bad_time_measure(
        data_trial_fix, max_t_task=5500)
    runs_na_glasses = missing_glasses(data_subject)

    invalid_runs = list(
        set(runs_incomplete_fix_task) |
        set(runs_bad_time_measure) |
        set(runs_na_glasses)
    )

    summary = pd.DataFrame(
        {'name': [
            'runs_incomplete_fix_task',
            'runs_bad_time_measure',
            'runs_na_glasses',
            'total'
        ],
            'length': [
                len(runs_incomplete_fix_task),
                len(runs_bad_time_measure),
                len(runs_na_glasses),
                len(invalid_runs)
            ]}
    )

    print(
        f"""Invalid runs for fix task: \n"""
        f"""{summary} \n"""
    )

    return invalid_runs
