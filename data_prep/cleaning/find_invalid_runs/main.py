import numpy as np
import pandas as pd

from data_prep.cleaning.find_invalid_runs.choice import filter_hit_ratio
from data_prep.cleaning.find_invalid_runs.both_tasks import filter_runs_no_instruction, \
    filter_full_but_no_et_data, filter_runs_low_fps, \
    filter_wrong_glasses
from data_prep.cleaning.find_invalid_runs.choice import filter_runs_not_us, filter_runs_precision, filter_runs_offset, \
    filter_bad_log_k
from data_prep.cleaning.find_invalid_runs.fix import runs_with_incomplete_fix_tasks, filter_runs_bad_time_measure, \
    missing_glasses
from utils.save_data import write_csv


def invalid_runs_global(
    data_trial, data_et, data_subject,
    max_t_task=5500,
    min_fps=3):
    print(f"""Clean runs that are otherwise not valid: """)

    # Not enough trials
    subjects_full_trial = data_trial \
        .loc[data_trial['trial_type_new'] == 'end', 'run_id'] \
        .unique()
    print(f'n={len(subjects_full_trial)} runs with full trials. ')

    runs_not_full_trial = np.setdiff1d(
        data_trial['run_id'].unique(),
        subjects_full_trial)

    # Fixation task. No validation possible
    data_trial_fix = data_trial.loc[
        (data_trial['trial_type'] == 'eyetracking-fix-object') &
        (data_trial['trial_duration'] == 5000)]

    runs_incomplete_fix_task = runs_with_incomplete_fix_tasks(
        data_trial_fix)
    runs_bad_time_measure = filter_runs_bad_time_measure(
        data_trial_fix, max_t_task=max_t_task)

    runs_not_follow_instructions = \
        filter_runs_no_instruction(data_subject)
    runs_full_but_not_enough_et = \
        filter_full_but_no_et_data(data_et, data_trial)
    runs_low_fps = filter_runs_low_fps(
        data_trial, data_et, min_fps)
    runs_cannot_see = filter_wrong_glasses(data_subject)

    # Plotting saccades from the fix task showed no variance
    runs_no_saccade = [144, 171, 380]

    invalid_runs = list(
        set(runs_not_full_trial) |
        set(runs_incomplete_fix_task) |
        set(runs_bad_time_measure) |
        set(runs_not_follow_instructions) |
        set(runs_low_fps) |
        set(runs_cannot_see) |
        set(runs_no_saccade) |
        set(runs_full_but_not_enough_et)
    )

    n_runs = len(data_trial['run_id'].unique())

    summary = pd.DataFrame({
        'name': [
            'runs_not_full_trial',
            'runs_incomplete_fix_task',
            'runs_bad_time_measure',
            'runs_noInstruction',
            'runs_lowFPS',
            'runs_cannotSee',
            'runs_no_saccade',
            'runs_full_but_not_enough_et',
            'total'],
        'length': [
            len(runs_not_full_trial),
            len(runs_incomplete_fix_task),
            len(runs_bad_time_measure),
            len(runs_not_follow_instructions),
            len(runs_low_fps),
            len(runs_cannot_see),
            len(runs_no_saccade),
            len(runs_full_but_not_enough_et),
            len(invalid_runs)],
        'percent': [
            len(runs_not_full_trial) / n_runs,
            len(runs_incomplete_fix_task) / n_runs,
            len(runs_bad_time_measure) / n_runs,
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


def invalid_runs_fix(data_trial_fix, data_subject):
    runs_incomplete_fix_task = runs_with_incomplete_fix_tasks(
        data_trial_fix)
    runs_bad_time_measure = filter_runs_bad_time_measure(
        data_trial_fix, max_t_task=5500)

    invalid_runs = list(
        set(runs_incomplete_fix_task) |
        set(runs_bad_time_measure))

    summary = pd.DataFrame(
        {'name': [
            'runs_incomplete_fix_task',
            'runs_bad_time_measure',
            'total'
        ],
            'length': [
                len(runs_incomplete_fix_task),
                len(runs_bad_time_measure),
                len(invalid_runs)
            ]}
    )

    print(
        f"""Invalid runs for fix task: \n"""
        f"""{summary} \n"""
    )

    return invalid_runs
