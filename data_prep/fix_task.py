import os

import pandas as pd

from utils.data_frames import merge_by_index
from utils.path import makedir
from utils.tables import summarize_datasets


def create_fix_tasks_datasets():
    data_et = pd.read_csv(
        os.path.join('data', 'all_trials', 'cleaned', 'data_et.csv'))
    data_trial = pd.read_csv(
        os.path.join('data', 'all_trials', 'cleaned', 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join('data', 'all_trials', 'cleaned', 'data_subject.csv'))
    print('Data read from data/all_trials/cleaned: ')
    summarize_datasets(data_et, data_trial, data_subject)

    data_et = merge_by_index(data_et, data_trial,
                                 'task_nr', 'chin', 'chinFirst', 'trial_type',
                                 'trial_duration', 'trial_duration_exact', 'x_pos', 'y_pos',
                                 'window_width', 'window_height')

    if 'glasses_binary' in data_trial.columns:
        data_trial = data_trial.drop(columns=['glasses_binary'])
    data_trial = data_trial.merge(
        data_subject.loc[:, ['run_id', 'glasses_binary']],
        on='run_id',
        how='left')

    data_et_fix = data_et.loc[
                  (data_et['trial_type'] == 'eyetracking-fix-object') &
                  (data_et['trial_duration'] == 5000) &
                  (data_et['t_task'] > 1000), :
                  ]

    data_trial_fix = data_trial.loc[
        (data_trial['trial_type'] == 'eyetracking-fix-object') &
        (data_trial['trial_duration'] == 5000),
        [
            'run_id', 'prolificID', 'subject', 'chinFirst',
            'trial_index', 'task_nr', 'rt', 'stimulus', 'key_press',
            'time_elapsed', 'recorded_at', 'window_width', 'window_height',
            'success', 'chin', 'x_pos', 'y_pos', 'window_width_max',
            'window_height_max', 'window_diagonal_max', 'window_diagonal',
            't_startTrial', 'trial_duration_exact', 'task_nr_new',
            'trial_type_new', 'trial_type_nr', 'fixTask', 'withinTaskIndex',
            'x_count', 'fps', 'positionIndex', 'glasses_binary'
        ]
    ]

    makedir('data', 'fix_task', 'raw')
    data_et.to_csv(
        os.path.join('data', 'fix_task', 'raw', 'data_et.csv'),
        index=False, header=True)
    data_et_fix.to_csv(
        os.path.join('data', 'fix_task', 'raw', 'data_et_fix.csv'),
        index=False, header=True)
    data_trial.to_csv(
        os.path.join('data', 'fix_task', 'raw', 'data_trial.csv'),
        index=False, header=True)
    data_trial_fix.to_csv(
        os.path.join('data', 'fix_task', 'raw', 'data_trial_fix.csv'),
        index=False, header=True)
    data_subject.to_csv(
        os.path.join('data', 'fix_task', 'raw', 'data_subject.csv'),
        index=False, header=True)
    print('Datasets saved to data/fix_task/raw (fix task trials): ')
    summarize_datasets(data_et_fix, data_trial_fix, data_subject)

    print('Datasets saved to data/fix_task/raw (all trials): ')
    summarize_datasets(data_et, data_trial, data_subject)