import numpy as np
import pandas as pd

from utils.data_frames import merge_by_index
from utils.tables import write_csv


def filter_invalid_runs(data_trial, data_et, data_subject):

    print(
        f"""\n"""
        f"""Clean runs that are otherwise not valid: """)

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

    invalid_runs = list(
        set(subjects_not_full_trial) |
        set(runs_not_follow_instructions) |
        set(runs_low_fps) |
        set(runs_cannot_see) |
        set(runs_full_but_not_enough_et)
    )

    n_runs = len(data_trial['run_id'].unique())

    summary = pd.DataFrame(
       {'name': [
                   'subjects_not_full_trial',
                   'runs_noInstruction',
                   'runs_lowFPS',
                   'runs_cannotSee',
                   'runs_full_but_not_enough_et',
                   'total'
       ],
        'length': [
                    len(subjects_not_full_trial),
                    len(runs_not_follow_instructions),
                    len(runs_low_fps),
                    len(runs_cannot_see),
                    len(runs_full_but_not_enough_et),
                    len(invalid_runs)
               ],
        'percent': [
                    len(subjects_not_full_trial)/n_runs,
                    len(runs_not_follow_instructions)/n_runs,
                    len(runs_low_fps)/n_runs,
                    len(runs_cannot_see)/len(data_subject),
                    len(runs_full_but_not_enough_et)/n_runs,
                    len(invalid_runs)/n_runs
        ]
       }
    )

    print(
        f"""\n n={n_runs} runs in total. Invalid_runs: \n"""
        f"""{round(summary, 2)}""")

    write_csv(
        summary,
        'global_invalid_runs.csv',
        'results', 'tables')

    return invalid_runs


def filter_runs_no_instruction(data_subject):
    runs_no_instruction = data_subject.loc[
        (data_subject['keptHead'] == 0) |
        (data_subject['triedChin'] == 0),
        'run_id'
    ].reset_index(drop=True)

    rate_no_instruction = \
        len(runs_no_instruction) / len(data_subject)

    no_instruct = data_subject.loc[
        data_subject['run_id'].isin(runs_no_instruction),
        ['run_id', 'prolificID', 'keptHead', 'triedChin']
    ] \
        .drop_duplicates()

    print(
        f"""n={len(no_instruct)} """
        f"""({len(no_instruct['prolificID'].unique())} """
        f"""unique Prolific IDs, {round(100 * rate_no_instruction, 2)}%) """
        f"""runs either did not kept their head still or try the """
        f"""chin rest at all. """)

    return no_instruct


def filter_full_but_no_et_data(data_et, data_trial):
    runs_no_et_data = data_trial.loc[
        (~data_trial['run_id'].isin(data_et['run_id'].unique())) &
        (data_trial['trial_type_new'] == 'end'),
        'run_id'
    ].unique()

    print(
        f"""n={len(runs_no_et_data)} are complete but have no et data. """)

    runs_full = data_trial.loc[
        data_trial['trial_type_new'] == 'end', 'run_id'].unique()

    et_trials = data_trial.loc[
        data_trial['trial_type'].isin([
            'eyetracking-calibration',
            'eyetracking-fix-object',
            'eyetracking-choice']),
        ['run_id', 'trial_index', 'x_count']
    ]

    na_et_by_run = et_trials.loc[pd.isna(et_trials['x_count']), :
                   ].groupby(['run_id'], as_index=False).count()

    runs_not_enough_et_data = na_et_by_run.loc[
        na_et_by_run['trial_index'] > 10, 'run_id']

    runs_full_but_few_et = np.intersect1d(
        runs_not_enough_et_data,
        runs_full)

    runs_full_but_not_enough_et = list(
        set(runs_no_et_data) |
        set(runs_full_but_few_et)
    )

    print(
        f"""n={len(runs_full_but_few_et)} runs have >10 trials """
        f"""with no et data. """)

    return runs_full_but_not_enough_et


def filter_runs_low_fps(data_trial, data_et, min_fps):

    grouped = data_et.groupby(
            ['run_id', 'trial_index'],
            as_index=False)['x'].count() \
        .reset_index() \
        .rename(columns={'x': 'x_count'})

    data_trial = merge_by_index(data_trial, grouped, 'x_count')

    data_trial['fps'] = \
        1000 * data_trial['x_count'] / \
        data_trial['trial_duration_exact']

    grouped_runs = data_trial.groupby(
        ['run_id'],
        as_index=False)['fps'].mean()

    runs_low_fps = grouped_runs.loc[grouped_runs['fps'] < min_fps, 'run_id']

    rate_low_fps = \
        len(runs_low_fps) / len(grouped_runs['run_id'].unique())
    print(
        f"""n={len(runs_low_fps)} ({round(100 * rate_low_fps, 2)}%) """
        f"""runs with low fps (<{min_fps}). \n""")

    return runs_low_fps


def filter_wrong_glasses(data_subject):
    runs_cannot_see = data_subject.loc[
        (data_subject['sight'] == 'notCorrected') &
        (data_subject['glasses'] == 'longSight'),
        'run_id']

    print(
        f"""n={len(runs_cannot_see)} runs that are long sighted """
        f"""but do not wear visual aids. """)

    return runs_cannot_see


def clean_runs(data, excluded_runs, name):

    data_raw = data

    data = data_raw.loc[~data_raw['run_id'].isin(excluded_runs), :]

    print(
        f"""Removing invalid runs from {name}: \n"""
        f"""   Raw: {len(data_raw['run_id'].unique())} \n"""
        f"""   Cleaned: {len(data['run_id'].unique())} \n""")

    return data
