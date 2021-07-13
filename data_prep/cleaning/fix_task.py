import numpy as np
import pandas as pd

from data_prep.cleaning.drop_invalid_data.runs import clean_runs
from data_prep.cleaning.drop_invalid_data.trials import clean_trial_duration
from utils.save_data import load_all_three_datasets, save_all_three_datasets


def clean_data_fix(
        max_t_task, exclude_runs=None, max_offset=None,
        data_et=None, data_trial=None, data_subject=None,
        path_origin=None, path_target=None):

    print('################################### \n'
          'Clean fix task datasets \n'
          '################################### \n')

    if path_origin is not None:
        data_et, data_trial, data_subject = load_all_three_datasets(path_origin)

    # Screening
    show_empty_fix_trials(data_trial)
    show_trials_high_t_task(data_trial, max_t_task=max_t_task)

    data_trial = clean_trial_duration(data_trial, 0, max_t_task, 'data_trial')
    data_et = clean_trial_duration(data_et, 0, max_t_task, 'data_et')

    if max_offset is not None:
        runs_high_offset = data_subject.loc[data_subject['offset'] > max_offset,
                                            'run_id']

        print(f"""Exclude {len(runs_high_offset)} for offset > {max_offset} """
              f"""({runs_high_offset})""")

        data_subject = clean_runs(data_subject, runs_high_offset, name='data_subject')
        data_et = clean_runs(data_et, runs_high_offset, name='data_et')
        data_trial = clean_runs(data_trial, runs_high_offset, name='data_trial')

    if exclude_runs is not None:
        data_subject = clean_runs(data_subject, exclude_runs, name='data_subject')
        data_et = clean_runs(data_et, exclude_runs, name='data_et')
        data_trial = clean_runs(data_trial, exclude_runs, name='data_trial')

    if path_target is not None:
        save_all_three_datasets(data_et, data_trial, data_subject, path_target)

    return data_et, data_trial, data_subject


def show_empty_fix_trials(data_trial_fix):

    null_data = data_trial_fix[pd.isna(data_trial_fix['x_count'])]

    if len(null_data) > 0:
        print(
            f"""n = {len(null_data)} fixation trials with no et_data: """
            f"""{null_data} \n""")
    else:
        print(f"""No fixation trials without et_data found """)


def show_trials_high_t_task(data_trial, max_t_task):
    grouped_time_by_trial = data_trial.loc[
                            data_trial['trial_duration_exact'] > max_t_task, :] \
                                .groupby(['run_id', 'trial_index']).mean() \
                                .reset_index() \
                                .loc[:, ['run_id', 'trial_index', 'trial_duration_exact']]

    if len(grouped_time_by_trial) > 0:
        print(f"""{len(grouped_time_by_trial)} very long trials: \n"""
              f"""{grouped_time_by_trial} \n""")
    else:
        print(f"""All trials are shorter than {max_t_task}ms """)
