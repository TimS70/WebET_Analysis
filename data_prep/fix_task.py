import os

import pandas as pd

from data_prep.add_variables.trial import merge_count_by_index
from utils.data_frames import merge_by_index, merge_mean_by_subject
from utils.path import makedir
from utils.tables import summarize_datasets, load_all_three_datasets, save_all_three_datasets


def create_fix_tasks_datasets():

    print('################################### \n'
          'Create fix task dataset \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'all_trials', 'cleaned'))

    data_et = merge_by_index(data_et, data_trial,
                                 'task_nr', 'chin', 'chinFirst', 'trial_type',
                                 'trial_duration', 'trial_duration_exact', 'x_pos', 'y_pos',
                                 'window_width', 'window_height')
    data_trial = merge_count_by_index(data_trial, data_et, 'x')
    data_trial = merge_mean_by_subject(data_trial, data_subject, 'glasses_binary')

    print('for the fixation task, gaze points after 1000ms were selected. \n')
    data_et = data_et.loc[
                  (data_et['trial_type'] == 'eyetracking-fix-object') &
                  (data_et['trial_duration'] == 5000) &
                  (data_et['t_task'] > 1000), :
                  ]

    data_trial = data_trial.loc[
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
            'x_count', 'fps', 'glasses_binary'
        ]
    ]

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'fix_task', 'raw'))
