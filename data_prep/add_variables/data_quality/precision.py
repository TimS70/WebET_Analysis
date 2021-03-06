import numpy as np
import pandas as pd

from utils.combine import merge_by_index
from utils.euclidean import euclidean_distance


def merge_xy_means(data):
    grouped = data \
        .groupby(['run_id', 'trial_index'], as_index=False) \
        .agg(x_mean=('x', 'mean'),
             y_mean=('y', 'mean'))

    data = merge_by_index(data, grouped, 'x_mean', 'y_mean')

    return data


def distance_from_xy_mean_square(data):
    data = merge_xy_means(data)
    data['distance_from_xy_mean_square'] = np.power(
        euclidean_distance(data['x'], data['x_mean'],
                           data['y'], data['y_mean']),
        2)

    data['distance_from_xy_mean_square_px'] = np.power(euclidean_distance(
        (data['x'] * data['window_width']),
        (data['x_mean'] * data['window_width']),
        (data['y'] * data['window_height']),
        (data['y_mean'] * data['window_height'])), 2)

    missing_values = data.loc[
        pd.isna(data['distance_from_xy_mean_square']),
        ['x', 'y', 'x_pos', 'y_pos', 'distance_from_xy_mean_square']]

    summary = data[['distance_from_xy_mean_square',
                    'distance_from_xy_mean_square_px']].describe()

    print(f"""Squared distance from the average: \n"""
          f"""{round(summary, 2)} \n""")

    if len(missing_values) > 0:
        print(f"""! Attention: Missing values: \n"""
              f"""{missing_values} \n \n """)

    else:
        print(" - No missing values found. \n")

    return data


def aggregate_precision_from_et_data(data_trial, data_et):
    grouped = data_et.groupby(['run_id', 'trial_index'], as_index=False)[[
        'distance_from_xy_mean_square',
        'distance_from_xy_mean_square_px']].mean()
    grouped = grouped.assign(
        precision=np.sqrt(grouped['distance_from_xy_mean_square']),
        precision_px=np.sqrt(grouped['distance_from_xy_mean_square_px']))

    data_trial = merge_by_index(data_trial, grouped,
                                'precision', 'precision_px')

    missing_values = data_trial.loc[
        pd.notna(data_trial['x_pos']) &
        pd.isna(data_trial['precision']),
        ['run_id', 'trial_index', 'x_pos', 'y_pos', 'precision']]

    print(f"""Precision: \n"""
          f"""{round(data_trial[['precision', 'precision_px']].describe(), 
                     2)} \n""")

    if len(missing_values) > 0:
        print(f"""! Attention: Missing values: \n"""
              f"""{missing_values} \n""")

    return data_trial
