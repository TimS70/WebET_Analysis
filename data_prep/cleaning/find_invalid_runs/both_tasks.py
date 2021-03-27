import numpy as np
import pandas as pd

from utils.combine_frames import merge_by_index


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

    na_et_by_run = et_trials \
        .loc[pd.isna(et_trials['x_count'])] \
        .groupby(['run_id'], as_index=False).count()

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
