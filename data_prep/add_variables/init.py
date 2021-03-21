import os

import pandas as pd

from data_prep.add_variables.eye_tracking import invert_y_axis
from data_prep.add_variables.subject import add_fps_subject_level, add_max_trials, \
    add_glasses_binary, add_recorded_date, add_employment_status, add_full_time_binary
from data_prep.add_variables.trial import add_fps_trial_level, merge_count_by_index, invert_y_pos, \
    add_position_index, add_window_size, add_exact_trial_duration, add_new_task_nr, add_trial_type_new, add_fix_task, \
    add_within_task_index
from utils.path import makedir
from utils.tables import summarize_datasets, load_all_three_datasets, save_all_three_datasets


def global_add_variables_to_datasets():

    print('################################### \n'
          'Create global variables \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'all_trials', 'combined'))

    n_approved_unique = len(
        data_subject.loc[data_subject['status'] == 'APPROVED',
                         'prolificID'].unique())

    n_approved = len(data_subject.loc[
                     data_subject['status'] == 'APPROVED', :])

    print(f"""Number of approved runs: """
          f"""n={n_approved_unique} unique participants """
          f"""({n_approved} approved IDs, incl. duplicates). \n""")

    data_et = invert_y_axis(data_et)

    data_trial = merge_count_by_index(data_trial, data_et, 'x')
    data_trial = invert_y_pos(data_trial)
    data_trial = add_position_index(data_trial)
    data_trial = add_window_size(data_trial)
    data_trial = add_exact_trial_duration(data_trial)
    data_trial = add_new_task_nr(data_trial)
    data_trial = add_trial_type_new(data_trial)
    data_trial = add_fix_task(data_trial)
    data_trial = add_within_task_index(data_trial)
    data_trial = add_fps_trial_level(data_trial)

    data_subject = add_fps_subject_level(data_subject, data_trial)
    data_subject = add_max_trials(data_subject, data_trial)
    data_subject = add_glasses_binary(data_subject)
    data_subject = add_recorded_date(data_subject, data_trial)
    data_subject = add_employment_status(data_subject)
    data_subject = add_full_time_binary(data_subject)

    save_all_three_datasets(
        data_et, data_trial, data_subject,
        os.path.join('data', 'all_trials', 'added_var'))
