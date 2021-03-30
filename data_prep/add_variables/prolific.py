import os

import pandas as pd

from analysis.choice_task.test_clusters import test_transition_clusters
from data_prep.add_variables.both_tasks.subject import add_fps_subject_level, \
    add_max_trials, \
    add_glasses_binary, add_recorded_date, add_employment_status, \
    add_full_time_binary
from data_prep.add_variables.both_tasks.trial import add_fps_trial_level, \
    add_window_size, \
    add_exact_trial_duration, add_new_task_nr, add_trial_type_new, add_fix_task, \
    add_within_task_index
from data_prep.add_variables.choice.aoi import create_aoi_columns, \
    match_remaining_et_trials, \
    add_aoi_counts_on_trial_level, add_fixation_counter, \
    count_fixations_on_trial_level, add_quadrant, add_aoi
from data_prep.add_variables.choice.behavior import choice_response_variables, \
    add_mean_choice_rt
from data_prep.add_variables.choice.choice_options import \
    identify_amount_left, add_choice_options_num, \
    reformat_attributes, add_k, top_bottom_attributes
from data_prep.add_variables.choice.et_indices import add_et_indices
from data_prep.add_variables.choice.eye_tracking import add_et_indices_subject
from utils.combine import merge_mean_by_subject, merge_by_index
from utils.save_data import load_all_three_datasets, save_all_three_datasets, \
    write_csv


def add_prolific_variables(path_origin, path_target):
    data_subject = pd.read_csv(path_origin)
    data_subject = add_employment_status(data_subject)
    data_subject = add_full_time_binary(data_subject)
    write_csv(path_target)