import numpy as np
import pandas as pd

from utils.combine import merge_by_index, merge_by_subject
from visualize.fix_task.main import plot_hit_means_per_dot


def add_hit_ratio(data_trial, data_et, max_offset=0.10,
                  min_hit_ratio=0.8):
    data_et = data_et \
        .assign(hit=(data_et['offset'] < max_offset).astype(int))

    grouped = data_et \
        .groupby(['run_id', 'trial_index'], as_index=False) \
        .agg(n=('x', 'count'),
             hit_mean=('hit', 'mean'))

    plot_hit_means_per_dot(grouped, max_offset)

    grouped = grouped.assign(
        hit_suffice=(grouped['hit_mean'] >= min_hit_ratio).astype(int))

    data_trial = merge_by_index(data_trial, grouped,
                                'hit_mean', 'hit_suffice')

    low_hits = grouped[grouped['hit_mean'] < 0.1]
    grouped = low_hits \
        .groupby(['run_id'], as_index=False) \
        .agg(n_trials=('trial_index', 'count'))

    print(f"""No gaze points at all: \n"""
          f"""N={len(low_hits['run_id'].unique())} runs """
          f"""with on average {round(grouped['n_trials'].mean(), 2)} """
          f"""trials. \n"""
          f"""{low_hits} \n""")

    return data_trial


def add_n_valid_dots(data_subject, data_trial):
    grouped = data_trial[data_trial['chin'] == 1] \
        .groupby(['run_id'], as_index=False) \
        .agg(n_valid_dots=('hit_suffice', 'sum'))

    data_subject = merge_by_subject(data_subject, grouped, 'n_valid_dots')
    data_subject['hit_ratio'] = data_subject['n_valid_dots'] / 9

    freq_table = pd.crosstab(
        index=data_subject['n_valid_dots'],
        columns="count")

    print(f"""How many dots are valid per subject. Dots during """
          f"""chin-rest validation: \n"""
          f"""{data_subject['n_valid_dots'].describe()} \n\n"""
          f"""{freq_table} \n\n"""
          f"""{data_subject[['run_id', 'fps', 'n_valid_dots']]}""")
    return data_subject


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
        (data_et['y_pos'] * data_et['window_height']))

    summary = data_et[['offset', 'offset_px']].describe()

    print(f"""Offset: \n"""
          f"""{round(summary, 2)} \n""")

    return data_et


def add_grand_mean_offset(data_subject, data_trial, data_et):
    grouped_mean = data_et \
        .groupby(['run_id', 'trial_index'], as_index=False) \
        .agg(x_mean=('x', 'mean'),
             y_mean=('y', 'mean'))

    data_trial = merge_by_index(data_trial, grouped_mean,
                                'x_mean', 'y_mean')

    data_trial['x_bias'] = data_trial['x_pos'] - data_trial['x_mean']
    data_trial['y_bias'] = data_trial['y_pos'] - data_trial['y_mean']

    data_trial['grand_offset'] = euclidean_distance(
        data_trial['x_mean'], data_trial['x_pos'],
        data_trial['y_mean'], data_trial['y_pos'])

    grouped = data_trial \
        .groupby(['run_id', 'trial_index'], as_index=False) \
        .agg(x_bias=('x_bias', 'mean'),
             y_bias=('y_bias', 'mean'),
             grand_offset=('grand_offset', 'mean'))

    data_subject = merge_by_subject(data_subject, grouped,
                                    'x_bias', 'y_bias', 'grand_offset')

    summary = data_subject[['x_bias', 'y_bias', 'grand_offset']].describe()

    print(f"""Added grand mean offset: \n"""
          f"""{summary} \n""")

    return data_subject, data_trial
