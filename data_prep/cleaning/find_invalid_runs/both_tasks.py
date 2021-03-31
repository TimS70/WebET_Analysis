import numpy as np
import pandas as pd

from utils.combine import merge_by_index


def filter_runs_no_instruction(data_subject):
    runs_no_instruction = data_subject.loc[
        (data_subject['keptHead'] == 0) |
        (data_subject['triedChin'] == 0),
        'run_id'].unique()

    rate_no_instruction = len(runs_no_instruction) / len(data_subject)

    no_instruct = data_subject.loc[
        data_subject['run_id'].isin(runs_no_instruction),
        ['run_id', 'prolificID', 'keptHead', 'triedChin']
    ] \
        .drop_duplicates()

    if len(no_instruct) > 0:
        print(f"""n={len(no_instruct)} """
              f"""({len(no_instruct['prolificID'].unique())} """
              f"""unique Prolific IDs, {round(100 * rate_no_instruction, 2)}%) """
              f"""runs either did not kept their head still or try the """
              f"""chin rest at all. """)
    else:
        print('All participants followed the instructions ')

    return no_instruct['run_id'].unique()


def filter_full_but_no_et_data(data_et, data_trial, max_missing_et):
    runs_no_et_data = data_trial.loc[
        (~data_trial['run_id'].isin(data_et['run_id'].unique())) &
        (data_trial['trial_type_new'] == 'end'),
        'run_id'].unique()

    if len(runs_no_et_data) > 0:
        print(f"""n={len(runs_no_et_data)} are complete but have no et data """)
    else:
        print('All complete runs also have eye-tracking data ')

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
        na_et_by_run['trial_index'] > max_missing_et, 'run_id']

    runs_full_but_few_et = np.intersect1d(
        runs_not_enough_et_data,
        runs_full)

    runs_full_but_not_enough_et = list(
        set(runs_no_et_data) |
        set(runs_full_but_few_et)
    )

    if len(runs_full_but_few_et) > 0:
        print(f"""n={len(runs_full_but_few_et)} runs have >{max_missing_et} """
              f"""trials with no et data. """)
    else:
        print(f"""No run has >{max_missing_et} trials with no et data """)

    return runs_full_but_not_enough_et


def filter_runs_low_fps(data_trial, data_et, min_fps):
    grouped = data_et \
        .groupby(['run_id', 'trial_index'], as_index=False) \
        .agg(x_count=('x', 'count'))

    data_trial = merge_by_index(data_trial, grouped, 'x_count')

    grouped = data_trial \
        .assign(fps=1000 * data_trial['x_count'] / \
                    data_trial['trial_duration_exact']) \
        .groupby(['run_id'], as_index=False) \
        .agg(fps=('fps', 'mean'))

    runs_low_fps = grouped.loc[grouped['fps'] < min_fps, 'run_id']

    return runs_low_fps


def filter_wrong_glasses(data_subject):
    runs_cannot_see = data_subject.loc[
        (data_subject['sight'] == 'notCorrected') &
        (data_subject['glasses'] == 'longSight'),
        'run_id']

    if len(runs_cannot_see) > 0:
        print(f"""n={len(runs_cannot_see)} runs that are long sighted """
             f"""but do not wear visual aids. """)
    else:
        print('All participants have the appropriate correction or perfect '
              'sight ')

    return runs_cannot_see
