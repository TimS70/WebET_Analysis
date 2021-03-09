import os

import numpy as np
import pandas as pd

from analysis.fix_task.fix_task import outcome_over_trials, compare_conditions_subject, grand_mean_offset, \
    check_gaze_saccade
from analysis.fix_task.positions import compare_positions

from utils.data_frames import merge_mean_by_index, merge_by_subject
from utils.tables import summarize_datasets




def add_data_quality_var():
    data_et = pd.read_csv(
        os.path.join('data', 'fix_task', 'cleaned', 'data_et.csv'))
    data_et_fix = pd.read_csv(
        os.path.join('data', 'fix_task', 'cleaned', 'data_et_fix.csv'))
    data_trial_fix = pd.read_csv(
        os.path.join('data', 'fix_task', 'cleaned', 'data_trial_fix.csv'))
    data_trial = pd.read_csv(
        os.path.join('data', 'fix_task', 'cleaned', 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join('data', 'fix_task', 'cleaned', 'data_subject.csv'))
    print('Datasets read from data/fix_task/cleaned (all trials): ')
    summarize_datasets(data_et, data_trial, data_subject)

    print('Datasets read from data/fix_task/cleaned (fix trials): ')
    summarize_datasets(data_et_fix, data_trial_fix, data_subject)


    # Only for dev
    data_trial = data_trial.loc[data_trial['run_id'] < 50, :]
    data_trial_fix = data_trial_fix.loc[
                     data_trial_fix['run_id'] < 50, :]

    data_et = data_et.loc[data_et['run_id'] < 50, :]
    data_et_fix = data_et_fix.loc[data_et_fix['run_id'] < 50, :]

    # # Offset

    # data_et = add_offset(data_et)
    # data_et_fix = add_offset(data_et_fix)
    # check_gaze_saccade(data_et, data_trial)
    #
    # data_trial = merge_mean_by_index(
    #     data_trial, data_et, 'offset', 'offset_px')
    # data_trial_fix = merge_mean_by_index(
    #     data_trial_fix, data_et_fix, 'offset', 'offset_px')
    #
    # outcome_over_trials(data_trial_fix, 'offset')
    # compare_positions(data_trial_fix, 'offset')
    #
    # data_subject = merge_by_subject(
    #     data_subject, data_trial_fix, 'offset', 'offset_px')
    #
    # compare_conditions_subject(data_subject, data_trial_fix, 'offset')
    # data_trial_fix = grand_mean_offset(data_et_fix, data_trial_fix)

    # # Precision
    # data_et = distanceFromAVG_square(data_et)
    # data_et_fix = distanceFromAVG_square(data_et_fix)
    #
    # data_trial = aggregate_precision_from_et_data(data_trial, data_et)
    # data_trial_fix = aggregate_precision_from_et_data(
    #     data_trial_fix, data_et_fix)
    # data_subject = merge_by_subject(
    #     data_subject, data_trial_fix, 'precision', 'precision_px')
    #
    # outcome_over_trials(data_trial_fix, 'precision')
    # compare_positions(data_trial_fix, 'precision')
    # compare_conditions_subject(data_subject, data_trial_fix, 'precision')


def euclidean_distance(x, x_target, y, y_target):
    x_diff = x - x_target
    y_diff = y - y_target
    euclideanDistance = np.sqrt(x_diff ** 2 + y_diff ** 2)
    return euclideanDistance


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
        f"""{data_et[['offset', 'offset_px']].describe()} \n""")

    return data_et


def merge_xy_means(data):
    grouped = data.groupby(['run_id', 'trial_index'])['x', 'y'].mean() \
        .rename(columns={'x': 'x_mean', 'y': 'y_mean'})

    if 'x_mean' in data.columns:
        data = data.drop(columns=['x_mean'])
    if 'y_mean' in data.columns:
        data = data.drop(columns=['y_mean'])
    data = data.merge(grouped, on=['run_id', 'trial_index'], how='left')
    return (data)


def distanceFromAVG_square(data):
    data = merge_xy_means(data)
    data['distanceFromAVG_square'] = np.power(
        euclidean_distance(data['x'], data['x_mean'], data['y'], data['y_mean']),
        2
    )
    data['distanceFromAVG_square_px'] = np.power(euclidean_distance(
        (data['x'] * data['window_width']),
        (data['x_mean'] * data['window_width']),
        (data['y'] * data['window_height']),
        (data['y_mean'] * data['window_height'])
    ), 2)

    missing_values = data.loc[
        pd.isna(data['distanceFromAVG_square']),
        ['x', 'y', 'x_pos', 'y_pos', 'distanceFromAVG_square']
    ]

    summary = data.loc[
              :, ['distanceFromAVG_square', 'distanceFromAVG_square_px']] \
        .describe()

    print(
        f"""Check for missing values: \n"""
        f"""{missing_values} \n \n """
        f"""Squared distance from the average: \n"""
        f"""{summary}"""
    )

    return data


def aggregate_precision_from_et_data(data_trial, data_et):
    data_trial = merge_mean_by_index(
        data_trial, data_et,
        'distanceFromAVG_square', 'distanceFromAVG_square_px')
    data_trial['precision'] = np.sqrt(data_trial['distanceFromAVG_square'])
    data_trial['precision_px'] = np.sqrt(data_trial['distanceFromAVG_square_px'])

    missing_values = data_trial.loc[
        pd.isna(data_trial['precision']),
        ['run_id', 'trial_index', 'x_pos', 'y_pos', 'precision']
    ]
    print(
        f"""Precision: \n"""
        f"""{data_trial['precision'].describe()} \n \n"""
        f"""{data_trial['precision_px'].describe()} \n""")

    if len(missing_values) > 0:
        print(
            f"""Missing values: \n"""
            f"""{missing_values} \n"""
        )

    return data_trial
