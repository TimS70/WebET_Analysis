import os

import numpy as np
import pandas as pd

from analysis.fix_task.data_quality import outcome_over_trials_vs_chin
from analysis.fix_task.positions import compare_positions

from utils.data_frames import merge_mean_by_index, merge_by_subject
from utils.path import makedir
from utils.tables import summarize_datasets, load_all_three_datasets, save_all_three_datasets


def add_data_quality():
    print('################################### \n'
          'Calculate data quality variables \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'fix_task', 'cleaned'))

    # Offset
    data_et = add_offset(data_et)
    data_trial = merge_mean_by_index(data_trial, data_et,
                                     'offset', 'offset_px')
    data_subject = merge_by_subject(data_subject, data_trial,
                                    'offset', 'offset_px')

    # Precision
    data_et = distance_from_xy_mean_square(data_et)
    data_trial = aggregate_precision_from_et_data(data_trial, data_et)
    data_subject = merge_by_subject(data_subject, data_trial,
                                    'precision', 'precision_px')

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'fix_task', 'added_var'))


def euclidean_distance(x, x_target, y, y_target):
    x_diff = x - x_target
    y_diff = y - y_target
    output = np.sqrt(x_diff ** 2 + y_diff ** 2)

    return output


def add_offset(data_et):
    data_et.loc[:, "offset"] = euclidean_distance(
        data_et["x"], data_et['x_pos'],
        data_et["y"], data_et['y_pos'])

    data_et.loc[:, "offset_px"] = euclidean_distance(
        (data_et["x"] * data_et['window_width']),
        (data_et['x_pos'] * data_et['window_width']),
        (data_et["y"] * data_et['window_height']),
        (data_et['y_pos'] * data_et['window_height'])
    )

    print(
        f"""Offset: \n"""
        f"""{round(data_et[['offset', 'offset_px']].describe(), 2)} \n""")

    return data_et


def merge_xy_means(data):
    grouped = data.groupby(
        ['run_id', 'trial_index'])[['x', 'y']].mean() \
        .rename(columns={'x': 'x_mean', 'y': 'y_mean'})

    if 'x_mean' in data.columns:
        data = data.drop(columns=['x_mean'])
    if 'y_mean' in data.columns:
        data = data.drop(columns=['y_mean'])
    data = data.merge(grouped, on=['run_id', 'trial_index'], how='left')

    return data


def distance_from_xy_mean_square(data):
    data = merge_xy_means(data)
    data['distance_from_xy_mean_square'] = np.power(
        euclidean_distance(data['x'], data['x_mean'], data['y'], data['y_mean']),
        2
    )
    data['distance_from_xy_mean_square_px'] = np.power(euclidean_distance(
        (data['x'] * data['window_width']),
        (data['x_mean'] * data['window_width']),
        (data['y'] * data['window_height']),
        (data['y_mean'] * data['window_height'])
    ), 2)

    missing_values = data.loc[
        pd.isna(data['distance_from_xy_mean_square']),
        ['x', 'y', 'x_pos', 'y_pos', 'distance_from_xy_mean_square']
    ]

    summary = data.loc[:, [
        'distance_from_xy_mean_square', 'distance_from_xy_mean_square_px']] \
        .describe()

    print(
        f"""Squared distance from the average: \n"""
        f"""{round(summary, 2)} \n""")

    if len(missing_values) > 0:
        print(
            f"""! Attention: Missing values: \n"""
            f"""{missing_values} \n \n """)

    else:
        print(" - No missing values found. \n")

    return data


def aggregate_precision_from_et_data(data_trial, data_et):
    data_trial = merge_mean_by_index(
        data_trial, data_et,
        'distance_from_xy_mean_square', 'distance_from_xy_mean_square_px')
    data_trial['precision'] = np.sqrt(
        data_trial['distance_from_xy_mean_square'])
    data_trial['precision_px'] = np.sqrt(
        data_trial['distance_from_xy_mean_square_px'])

    missing_values = data_trial.loc[
        pd.notna(data_trial['x_pos']) &
        pd.isna(data_trial['precision']),
        ['run_id', 'trial_index', 'x_pos', 'y_pos', 'precision']
    ]
    print(
        f"""Precision: \n"""
        f"""{round(data_trial[['precision','precision_px']].describe(), 2)} \n""")

    if len(missing_values) > 0:
        print(
            f"""! Attention: Missing values: \n"""
            f"""{missing_values} \n"""
        )

    return data_trial
