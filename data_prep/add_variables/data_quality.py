import numpy as np
import pandas as pd


import os

import pandas as pd

from analysis.fix_task import plot_gaze_shift
from data_prep.add_variables.data_quality import add_offset
from data_prep.cleaning.fix_task import screen_fix_task, remove_high_tTask
from data_prep.cleaning.invalid_runs import clean_runs
from utils.data_frames import add_var_to_data_et, merge_by_index, merge_mean_by_index
from utils.tables import summarize_datasets


def add_data_quality_var():

    data_et = pd.read_csv(
        os.path.join('data', 'fix_task', 'cleaned', 'data_et.csv'))
    data_trial = pd.read_csv(
        os.path.join('data', 'fix_task', 'cleaned', 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join('data', 'fix_task', 'cleaned', 'data_subject.csv'))
    summarize_datasets(data_et, data_trial, data_subject)

    data_trial_fix = data_trial_fix.loc[pd.notna(data_trial_fix['x_count']), :]

    data_et = add_offset(data_et)
    data_et_fix = add_offset(data_et_fix)

    plot_gaze_shift(data_et, data_trial)

    data_trial = merge_mean_by_index(data_trial, data_et,
                                     'offset', 'offset_px')
    data_trial_fix = merge_mean_by_index(data_trial_fix, data_et_fix,
                                         'offset', 'offset_px')




def euclideanDistance(x, x_target, y, y_target):
    x_diff = x - x_target
    y_diff = y - y_target
    euclideanDistance = np.sqrt(x_diff**2 + y_diff**2)
    return euclideanDistance


def add_offset(data_et):
    data_et.loc[:, "offset"] = euclideanDistance(
            data_et["x"], data_et['x_pos'],
            data_et["y"], data_et['y_pos'])

    data_et.loc[:, "offset_px"] = euclideanDistance(
        (data_et["x"] * data_et['window_width']),
        (data_et['x_pos'] * data_et['window_width']),
        (data_et["y"] * data_et['window_height']),
        (data_et['y_pos'] * data_et['window_height'])
    )

    print(
        f"""Offset: \n"""
        f"""{data_et[['offset', 'offset_px']].describe()}""")

    return data_et