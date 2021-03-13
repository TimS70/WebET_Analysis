import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

from utils.data_frames import merge_by_index, merge_by_subject
from utils.path import makedir
from utils.tables import write_csv


def add_aoi_et(data_et, use_adjusted_et_data):
    # If not already done in Matlab
    if use_adjusted_et_data:
        data_et['aoi'] = data_et['aoi'].replace(
            [1, 2, 3, 4],
            ['TL', 'TR', 'BL', 'BR'])

    else:
        print(f"""AOI will be calculated. No cluster correction.""")
        data_et = add_aoi(data_et, 0.3, 0.3)

    freq_table = pd.crosstab(
        index=data_et['aoi'],
        columns="count")

    print(
        f"""Gaze points across AOIs: \n"""
        f"""{freq_table} \n""")
    plot_aoi_scatter(data_et)

    data_et = create_aoi_columns(data_et)

    return data_et


def add_aoi(data, aoi_width, aoi_height):
    aoi_centers = pd.DataFrame(
        [
            [(0.05 + 0.9 * 0.2), 0.75],
            [(0.05 + 0.9 * 0.8), 0.75],
            [(0.05 + 0.9 * 0.2), 0.25],
            [(0.05 + 0.9 * 0.8), 0.25]
        ],
        columns=['x', 'y'],
        index=['TL', 'TR', 'BL', 'BR']
    )

    data['aoi'] = 0
    for aoi in aoi_centers.index:
        data.loc[
            (data['x'] > (aoi_centers.loc[aoi, 'x'] - aoi_width / 2)) &
            (data['x'] < (aoi_centers.loc[aoi, 'x'] + aoi_width / 2)) &
            (data['y'] > (aoi_centers.loc[aoi, 'y'] - aoi_height / 2)) &
            (data['y'] < (aoi_centers.loc[aoi, 'y'] + aoi_height / 2)),
            'aoi'] = aoi
    return data


def match_remaining_et_trials(data_trial, data_et):

    grouped = data_et.groupby(
            ['run_id', 'trial_index'],
            as_index=False)[['x', 'y']].mean() \
        .rename(columns={'x': 'x_mean', 'y': 'y_mean'})

    data_trial = merge_by_index(data_trial, grouped, 'x_mean', 'y_mean')
    missing_values = data_trial.loc[
                     data_trial[['x_mean', 'y_mean']].isna().all(1), :] \
        .groupby(['run_id'], as_index=False)['trial_index'].count() \
        .rename(columns={'trial_index': 'n'})

    data_trial = data_trial.loc[
                 ~data_trial[['x_mean', 'y_mean']].isna().all(1), :]

    print(
        f"""data_trial: Removing trials with missing eye-tracking data: \n"""
        f"""k={sum(missing_values['n'])} trials of """
        f"""{missing_values['run_id'].nunique()} runs. \n"""
    )

    return data_trial


def match_remaining_et_runs(data, data_et, data_name):

    run_et_but_not_data = data.loc[
        ~data['run_id'].isin(data_et['run_id'].unique()), 'run_id'] \
        .unique()

    if len(run_et_but_not_data) > 0:
        print(
            f"""n={len(run_et_but_not_data)} ({run_et_but_not_data}) """
            f"""runs were in data_et but not in {data_name}. \n"""
        )

    data = data.loc[data['run_id'].isin(data_et['run_id'].unique()), :]

    return data


def plot_aoi_scatter(data_et):
    data_plot = data_et.loc[data_et['aoi'] != 0, ['x', 'y']]
    x = data_plot['x']
    y = data_plot['y']
    plt.scatter(x, y)
    plt.ylim(0, 1)
    plt.xlim(0, 1)
    makedir('results', 'plots', 'choice_task')
    plt.savefig(
        os.path.join('results', 'plots', 'choice_task',
                      'aoi_scatter.png'))
    plt.close()


def create_aoi_columns(data):
    data['aoi_aLL'] = 0
    data['aoi_tLL'] = 0
    data['aoi_aSS'] = 0
    data['aoi_tSS'] = 0

    # If amounts are on the left side
    ## If the gaze point is in the top option
    data.loc[((data['amountLeft'] == 1) & (data['LL_top'] == 1) & (data['aoi'] == 'TL')),
             'aoi_aLL'] = 1
    data.loc[((data['amountLeft'] == 1) & (data['LL_top'] == 1) & (data['aoi'] == 'TR')),
             'aoi_tLL'] = 1
    data.loc[((data['amountLeft'] == 1) & (data['LL_top'] == 1) & (data['aoi'] == 'BL')),
             'aoi_aSS'] = 1
    data.loc[((data['amountLeft'] == 1) & (data['LL_top'] == 1) & (data['aoi'] == 'BR')),
             'aoi_tSS'] = 1

    ## If the gaze point is in the bottom option
    data.loc[((data['amountLeft'] == 1) & (data['LL_top'] == 0) & (data['aoi'] == 'TL')),
             'aoi_aSS'] = 1
    data.loc[((data['amountLeft'] == 1) & (data['LL_top'] == 0) & (data['aoi'] == 'TR')),
             'aoi_tSS'] = 1
    data.loc[((data['amountLeft'] == 1) & (data['LL_top'] == 0) & (data['aoi'] == 'BL')),
             'aoi_aLL'] = 1
    data.loc[((data['amountLeft'] == 1) & (data['LL_top'] == 0) & (data['aoi'] == 'BR')),
             'aoi_tLL'] = 1

    # If amounts are on the right side
    ## If the gaze point is in the top option
    data.loc[((data['amountLeft'] == 0) & (data['LL_top'] == 1) & (data['aoi'] == 'TL')),
             'aoi_tLL'] = 1
    data.loc[((data['amountLeft'] == 0) & (data['LL_top'] == 1) & (data['aoi'] == 'TR')),
             'aoi_aLL'] = 1
    data.loc[((data['amountLeft'] == 0) & (data['LL_top'] == 1) & (data['aoi'] == 'BL')),
             'aoi_tSS'] = 1
    data.loc[((data['amountLeft'] == 0) & (data['LL_top'] == 1) & (data['aoi'] == 'BR')),
             'aoi_aSS'] = 1

    ## If the gaze point is in the bottom option
    data.loc[((data['amountLeft'] == 0) & (data['LL_top'] == 0) & (data['aoi'] == 'TL')),
             'aoi_tSS'] = 1
    data.loc[((data['amountLeft'] == 0) & (data['LL_top'] == 0) & (data['aoi'] == 'TR')),
             'aoi_aSS'] = 1
    data.loc[((data['amountLeft'] == 0) & (data['LL_top'] == 0) & (data['aoi'] == 'BL')),
             'aoi_tLL'] = 1
    data.loc[((data['amountLeft'] == 0) & (data['LL_top'] == 0) & (data['aoi'] == 'BR')),
             'aoi_aLL'] = 1
    return data


def add_aoi_counts_on_trial_level(data_trial, data_et):
    grouped = data_et.groupby(
        ['run_id', 'trial_index'])[['aoi_aSS', 'aoi_aLL',
                                    'aoi_tSS', 'aoi_tLL']].sum() \
        .reset_index()

    makedir('results', 'tables', 'aoi')
    write_csv(
        grouped,
        'aoi_by_run_and_trial.csv',
        'results', 'tables', 'aoi')

    aoi_over_trials = grouped.assign(
        aoi_n=grouped.loc[:, ['aoi_aSS', 'aoi_tSS', 'aoi_aLL', 'aoi_tLL']] \
        .sum(axis=1)) \
        .loc[:, 'aoi_n']

    plt.hist(aoi_over_trials, bins=20)

    makedir('results', 'plots', 'choice_task')
    plt.savefig(
        os.path.join('results', 'plots', 'choice_task', 'n_aoi_over_trials.png'))
    plt.close()

    for var in ['aoi_aSS', 'aoi_aLL', 'aoi_tSS', 'aoi_tLL']:
        if var in data_trial.columns:
            data_trial = data_trial.drop(columns=[var])

    data_trial = data_trial.merge(
        grouped,
        on=['run_id', 'trial_index'],
        how='left')

    print(
        f"""data_trial: Added AOI count on trial level."""
    )

    return data_trial


def add_fixation_counter(data):
    data = data.copy()
    data.loc[:, 'fix_counter'] = 0

    for subject in tqdm(
            data['run_id'].unique(),
            desc='Add fixation counter to data_et: '):
        for trial in data.loc[data['run_id'] == subject, 'withinTaskIndex'].unique():
            temp_aoi = data.loc[
                (data['run_id'] == subject) &
                (data['withinTaskIndex'] == trial),
                'aoi']

            data.loc[
                (data['run_id'] == subject) &
                (data['withinTaskIndex'] == trial),
                'fix_counter'] = fix_counter(temp_aoi)

    grouped_n_fix_by_aoi = data \
        .loc[data['aoi'].isin(['BL', 'BR', 'TL', 'TR']), :] \
        .groupby(
            ['aoi', 'run_id', 'trial_index'],
            as_index=False)['fix_counter'].nunique() \
        .rename(columns={'fix_counter': 'n'}) \
        .groupby(
            ['aoi'],
            as_index=False)['n'].sum()

    print(
        f"""data_et: Added fixation counter: \n"""
        f"""{grouped_n_fix_by_aoi}"""
    )

    return data


def fix_counter(aoi_vector):
    aoi_numbers = aoi_vector \
        .replace(['TL', 'TR', 'BL', 'BR'], np.arange(1, 5)) \
        .astype(int) \
        .reset_index(drop=True)
    counter = 0

    fix_counter_var = np.zeros(len(aoi_numbers))
    fix_counter_var[0] = int(aoi_numbers[0] != 0)

    for i in np.delete(aoi_numbers.index, 0):
        if (
                (aoi_numbers[i] > 0) &
                (aoi_numbers[i] != aoi_numbers[i - 1])
        ):
            counter += 1

        if aoi_numbers[i] > 0:
            fix_counter_var[i] = counter

    return fix_counter_var


def count_fixations_on_trial_level(data_trial, data_et):
    data_trial = data_trial \
        .merge(
            data_et.groupby(
                ['run_id', 'withinTaskIndex'])['fix_counter'].nunique(),
            on=['run_id', 'withinTaskIndex'],
            how='left') \
        .rename(columns={'n_fixations': 'fix_counter'})

    return data_trial
