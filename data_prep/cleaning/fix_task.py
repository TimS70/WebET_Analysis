import os

import numpy as np
import pandas as pd

from data_prep.cleaning.choice import clean_trial_duration
from data_prep.cleaning.find_invalid_runs.main import invalid_runs_fix
from utils.tables import load_all_three_datasets, save_all_three_datasets


def clean_fix_task_datasets():
    print('################################### \n'
          'Clean fix task datasets \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'fix_task', 'raw'))

    # Screening
    invalid_runs = invalid_runs_fix(data_trial, data_subject)

    data_trial = clean_runs(data_trial, invalid_runs, 'data_trial')
    data_et = clean_runs(data_et, invalid_runs, 'data_et')
    data_subject = clean_runs(data_subject, invalid_runs, 'data_subject')

    data_trial = clean_trial_duration(data_trial, 0, 5500, 'data_trial')
    data_et = clean_trial_duration(data_et, 0, 5500, 'data_et')

    data_trial = data_trial.loc[pd.notna(data_trial['x_count']), :]

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'fix_task', 'cleaned'))


def euclidean_distance(x, x_target, y, y_target):
    x_diff = x - x_target
    y_diff = y - y_target
    output = np.sqrt(x_diff ** 2 + y_diff ** 2)

    return output


def show_empty_fix_trials(data_trial_fix):
    null_data = data_trial_fix.loc[pd.isna(data_trial_fix['x_count']), :]

    if len(null_data) > 0:
        print(
            f"""n = {len(null_data)} fixation trials with no et_data: """
            f"""{null_data} \n""")
    else:
        print(f"""No fixation trials without et_data found. \n""")


def show_trials_high_t_task(data_trial, max_t_task):
    grouped_time_by_trial = data_trial.loc[
                            data_trial['trial_duration_exact'] > max_t_task, :] \
                                .groupby(['run_id', 'trial_index']).mean() \
                                .reset_index() \
                                .loc[:, ['run_id', 'trial_index', 'trial_duration_exact']]

    print(f"""k={len(grouped_time_by_trial)} very long trials: \n"""
          f"""{grouped_time_by_trial} \n""")
