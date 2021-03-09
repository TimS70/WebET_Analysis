import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils.path import makedir
from utils.tables import write_csv


def outcome_over_trials(data_trial, outcome):
    data_plot = group_chin_within_task_index(
        data_trial.loc[data_trial['fixTask'] == 1, :],
        outcome)

    plt.style.use('seaborn-whitegrid')
    fig, ax = plt.subplots(1, 2, sharey='none', figsize=(15, 6))
    fig.suptitle('chin==0 vs. chin==1')

    ax[0].set_ylim(0, 1)

    for i in [0, 1]:
        data = data_plot.loc[data_plot['chin'] == i, :]
        ax[i].errorbar(
            x=data['withinTaskIndex'],
            y=data[(outcome + '_median')],
            yerr=[data[(outcome + '_std_lower')],
                  data[(outcome + '_std_upper')]],
            fmt='^k:',
            capsize=5
        )
    makedir('results', 'plots', 'fix_task')
    plt.savefig(
        os.path.join('results', 'plots', 'fix_task',
                     (outcome + '_vs_trials.png')))
    plt.close()


def group_chin_within_task_index(data, var_name):
    df_m = data.groupby(
        ['chin', 'withinTaskIndex'])[var_name].median() \
        .reset_index() \
        .rename(columns={var_name: var_name + '_median'}) \
        .reset_index()

    data = data.merge(df_m, on=['chin', 'withinTaskIndex'], how='left')
    data['above_median'] = data[var_name] > data[var_name + '_median']

    df_std_upper = data.loc[data['above_median'] == 1, :] \
        .groupby(['chin', 'withinTaskIndex'])[var_name].median() \
        .reset_index() \
        .rename(columns={var_name: var_name + '_std_upper'}) \
        .reset_index()
    df_std_lower = data.loc[data['above_median'] == 0, :] \
        .groupby(['chin', 'withinTaskIndex'])[var_name].median() \
        .reset_index() \
        .rename(columns={var_name: var_name + '_std_lower'}) \
        .reset_index()

    output = pd.concat([
        df_m,
        df_std_upper[var_name + '_std_upper'],
        df_std_lower[var_name + '_std_lower']
    ], axis=1)

    return output


def grand_mean_offset(data_et_fix, data_trial_fix):
    grouped = data_et_fix.groupby(
        ['run_id', 'trial_index'],
        as_index=False)[['x', 'y']].mean() \
        .rename(columns={'x': 'x_mean', 'y': 'y_mean'})

    if 'x_mean' in data_trial_fix.columns:
        data_trial_fix = data_trial_fix.drop(columns=['x_mean'])
    if 'y_mean' in data_trial_fix.columns:
        data_trial_fix = data_trial_fix.drop(columns=['y_mean'])
    data_trial_fix = data_trial_fix.merge(
        grouped,
        on=['run_id', 'trial_index'],
        how='left'
    )
    data_trial_fix['x_mean_px'] = \
        data_trial_fix['x_mean'] * data_trial_fix['window_width']
    data_trial_fix['y_mean_px'] = \
        data_trial_fix['y_mean'] * data_trial_fix['window_height']
    data_trial_fix.loc[:, [
        'x_mean', 'x_mean_px',
        'y_mean', 'y_mean_px']].describe()

    data_trial_fix['grand_deviation'] = euclidean_distance(
        data_trial_fix['x_mean'], data_trial_fix['x_pos'],
        data_trial_fix['y_mean'], data_trial_fix['y_pos']
    )

    summary = data_trial_fix['grand_deviation'].describe()

    write_csv(
        summary,
        'offset_grand_deviation.csv',
        'results', 'tables', 'fix_task')

    print(
        f"""Grand mean deviation: \n"""
        f"""{summary} \n""")

    return data_trial_fix


def euclidean_distance(x, x_target, y, y_target):
    x_diff = x - x_target
    y_diff = y - y_target
    output = np.sqrt(x_diff ** 2 + y_diff ** 2)

    return output


def compare_conditions_subject(data_subject, data_trial_fix, outcome):
    data_subject = separate_outcomes_by_condition(
        data_subject, data_trial_fix, outcome, 'chin')

    data_subject = separate_outcomes_by_condition(
        data_subject, data_trial_fix, outcome, 'glasses_binary')

    summary = data_subject.loc[
              :,
              [
                  outcome, (outcome + '_chin_0'),
                  (outcome + '_chin_1'),
                  (outcome + '_glasses_binary_0'),
                  (outcome + '_glasses_binary_1')
              ]
              ].describe()

    write_csv(
        summary,
        (outcome + '_compare_glasses_chin_subject.csv'),
        'results', 'tables', 'fix_task')


def separate_outcomes_by_condition(data, large_data,
                                   var_name, var_condition):
    var_cond_0 = var_name + '_' + var_condition + '_0'
    var_cond_1 = var_name + '_' + var_condition + '_1'

    if var_cond_0 in data.columns:
        data = data.drop(columns=[var_cond_0])
    if var_cond_1 in data.columns:
        data = data.drop(columns=[var_cond_1])

    grouped = large_data \
        .groupby(['run_id', var_condition])[var_name].mean() \
        .reset_index() \
        .pivot(index='run_id',
               columns=var_condition,
               values=var_name) \
        .reset_index() \
        .rename(columns={0.0: var_cond_0, 1.0: var_cond_1})
    data = data.merge(
        grouped.loc[:, ['run_id', var_cond_0, var_cond_1]],
        on='run_id',
        how='left')

    return data
