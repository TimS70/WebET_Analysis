import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis.fix_task.gaze_saccade import check_gaze_saccade
from analysis.fix_task.main_effects import main_effects
from analysis.fix_task.positions import compare_positions
from analysis.fix_task.randomization import check_randomization
from analysis.fix_task.visualize_gaze import fix_heatmap, visualize_exemplary_run
from utils.data_frames import merge_by_index
from utils.path import makedir
from utils.tables import write_csv, summarize_datasets


def data_quality_analysis():
    data_et = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_et.csv'))
    data_et_fix = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_et_fix.csv'))
    data_trial_fix = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_trial_fix.csv'))
    data_trial = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_subject.csv'))

    print('Datasets read from data/fix_task/added_var (all trials): ')
    summarize_datasets(data_et, data_trial, data_subject)

    print('Datasets read from data/fix_task/added_var (fix trials): ')
    summarize_datasets(data_et_fix, data_trial_fix, data_subject)

    # Only for dev
    data_trial = data_trial.loc[data_trial['run_id'] < 50, :]
    data_trial_fix = data_trial_fix.loc[
                     data_trial_fix['run_id'] < 50, :]

    data_et = data_et.loc[data_et['run_id'] < 50, :]
    data_et_fix = data_et_fix.loc[data_et_fix['run_id'] < 50, :]
    data_subject = data_subject.loc[data_subject['run_id'] < 50, :]

    # check_gaze_saccade(data_et, data_trial)
    # compare_conditions_subject(
    #     data_subject, data_trial_fix, 'offset')
    # data_trial_fix = grand_mean_offset(
    #     data_et_fix, data_trial_fix)
    #
    # outcome_over_trials(data_trial_fix, 'precision')
    # compare_positions(data_trial_fix, 'precision')
    # compare_conditions_subject(
    #     data_subject, data_trial_fix, 'precision')

    # check_randomization(data_trial_fix)

    # main_effects(data_trial_fix, data_subject)

    fix_heatmap(data_et_fix)

    data_plot = merge_by_index(data_et_fix, data_trial_fix, 'chin')
    visualize_exemplary_run(
        data_plot.loc[
            (data_plot['run_id'] == 43) & (data_plot['chin'] == 0), :])


def outcome_over_trials(data_trial, outcome):
    data_plot = group_chin_withinTaskIndex(
        data_trial.loc[data_trial['fixTask'] == 1, :],
        outcome)

    plt.style.use('seaborn-whitegrid')
    fig, ax = plt.subplots(1, 2, sharey=True, figsize=(15, 6))
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


def group_chin_withinTaskIndex(data, varName):
    df_m = data.groupby(['chin', 'withinTaskIndex']) \
        [varName].median() \
        .reset_index() \
        .rename(columns={varName: varName + '_median'}) \
        .reset_index()

    data = data.merge(df_m, on=['chin', 'withinTaskIndex'], how='left')
    data['above_median'] = data[varName] > data[varName + '_median']

    df_std_upper = data.loc[data['above_median'] == 1, :] \
        .groupby(['chin', 'withinTaskIndex'])[varName].median() \
        .reset_index() \
        .rename(columns={varName: varName + '_std_upper'}) \
        .reset_index()
    df_std_lower = data.loc[data['above_median'] == 0, :] \
        .groupby(['chin', 'withinTaskIndex'])[varName].median() \
        .reset_index() \
        .rename(columns={varName: varName + '_std_lower'}) \
        .reset_index()

    output = pd.concat([
        df_m,
        df_std_upper[varName + '_std_upper'],
        df_std_lower[varName + '_std_lower']
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
    data_trial_fix.loc[:,
    ['x_mean', 'x_mean_px', 'y_mean', 'y_mean_px']].describe()

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


def separate_outcomes_by_condition(data, large_data, varName, varCondition):
    var_cond_0 = varName + '_' + varCondition + '_0'
    var_cond_1 = varName + '_' + varCondition + '_1'

    if var_cond_0 in data.columns:
        data = data.drop(columns=[var_cond_0])
    if var_cond_1 in data.columns:
        data = data.drop(columns=[var_cond_1])

    grouped = large_data \
        .groupby(['run_id', varCondition])[varName].mean() \
        .reset_index() \
        .pivot(index='run_id',
               columns=varCondition,
               values=varName) \
        .reset_index() \
        .rename(columns={0.0: var_cond_0, 1.0: var_cond_1})
    data = data.merge(
        grouped.loc[:, ['run_id', var_cond_0, var_cond_1]],
        on='run_id',
        how='left')

    return data
