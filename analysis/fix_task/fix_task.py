import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import os
import pandas as pd
import pingouin as pg
import seaborn as sns
import scipy
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import silhouette_score
from tqdm import tqdm

import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels.graphics.api as smg
import statsmodels.stats.multitest as smt
from statsmodels.formula.api import ols
import sys

from data_prep.add_variables.trial import add_position_index
from utils.data_frames import merge_by_index
from utils.path import makedir
from utils.tables import write_csv, view


def check_gaze_saccade(data_et, data_trial):
    data_et = merge_by_index(
        data_et, data_trial,
        'task_nr_new', 'chinFirst',
        'trial_duration', 'trial_duration_exact',
        'fixTask', 'positionIndex')

    data_et_cross_and_task = select_fix_cross_and_fix_task(data_et)
    data_trial_cross_and_task = select_fix_cross_and_fix_task(data_trial)

    data_et_cross_and_task = shift_t_task_for_fix_cross(
        data_et_cross_and_task)
    data_et_cross_and_task = new_yx_pos(
        data_et_cross_and_task)
    data_et_cross_and_task = new_position_index(
        data_et_cross_and_task)

    data_et_cross_and_task['offset'] = euclidean_distance(
        data_et_cross_and_task['x'],
        data_et_cross_and_task['new_x_pos'],
        data_et_cross_and_task['y'],
        data_et_cross_and_task['new_y_pos']
    )

    example = data_et_cross_and_task.loc[:,
              ['run_id', 'trial_index', 'fixTask',
               'x', 'y', 't_task',
               'x_pos', 'y_pos',
               'new_x_pos', 'new_y_pos', 'positionIndex',
               'offset']]

    write_csv(
        example,
        'check_saccade.csv',
        'results', 'tables', 'fix_task')

    print(
        f"""Is the offset correct? \n"""
        f"""{example.head(5)} \n"""
    )

    for subject in tqdm(
            data_et_cross_and_task['run_id'].unique(),
            desc='Plotting fix task saccades: '):
        plot_gaze_saccade(
            data_et_cross_and_task.loc[
            data_et_cross_and_task['run_id'] == subject, :
            ],
            ('offset' + str(subject) + '_gaze_shift.png')
        )


def plot_gaze_saccade(data_et_cross_and_task, file_name):
    average_line_no_chin = create_median_line(
        data_et_cross_and_task.loc[
        data_et_cross_and_task['chin'] == 0, :])
    print(average_line_no_chin)

    average_line_chin = create_median_line(
        data_et_cross_and_task.loc[
        data_et_cross_and_task['chin'] == 1, :])

    fig, axes = plt.subplots(
        nrows=1, ncols=2, sharey=True, figsize=(18, 12))
    fig.suptitle(
        'Median local offset for all subjects across a '
        'fixation task trial', fontsize=20)

    axes[0].set_title("Chin==0")
    axes[1].set_title("Chin==1")

    sns.scatterplot(ax=axes[0],
                    data=data_et_cross_and_task.loc[
                         data_et_cross_and_task['chin'] == 0, :],
                    x="t_task",
                    y="offset")

    sns.lineplot(ax=axes[0],
                 x=average_line_no_chin['t_task'],
                 y=average_line_no_chin['offset'],
                 color='r')

    sns.scatterplot(ax=axes[1],
                    data=data_et_cross_and_task.loc[
                         data_et_cross_and_task['chin'] == 1, :],
                    x="t_task",
                    y="offset")

    sns.lineplot(ax=axes[1],
                 x=average_line_chin['t_task'],
                 y=average_line_chin['offset'],
                 color='r')

    plt.setp(axes, xlim=(-1500, 5000))
    plt.xlabel("t_task")

    makedir('results', 'plots', 'fix_task', 'saccade')
    plt.savefig(
        os.path.join('results', 'plots', '', 'saccade',
                     file_name))
    plt.close()


def select_fix_cross_and_fix_task(data):
    data_cross_and_task = data.loc[
                          (data['trial_type'] == 'eyetracking-fix_object') &
                          (
                                  (data['chinFirst'] == 0) &
                                  (data['task_nr_new'].isin([1, 2]))
                          ) |
                          (
                                  (data['chinFirst'] == 1) &
                                  (data['task_nr_new'].isin([1, 3]))
                          ), :].reset_index(drop=True)

    return data_cross_and_task


def select_fixTask_and_fixCross(data):
    return data.loc[
           (data['trial_type'] == 'eyetracking-fix-object') &
           ((data['task_nr'] == 1) |
            ((data['chinFirst'] == 0) & (data['task_nr'] == 2)) |
            ((data['chinFirst'] == 1) & (data['task_nr'] == 3))
            ), :].reset_index(drop=True)


def shift_t_task_for_fix_cross(data):
    data.loc[
        (data['trial_type'] == 'eyetracking-fix-object') &
        (data['fixTask'] == 0) &
        (data['trial_duration'] == 1500),
        't_task'
    ] = data.loc[
            (data['trial_type'] == 'eyetracking-fix-object') &
            (data['fixTask'] == 0) &
            (data['trial_duration'] == 1500),
            't_task'] - 1500

    return data


def new_yx_pos(data_et):
    data_et['new_x_pos'] = data_et['x_pos']
    data_et['new_y_pos'] = data_et['y_pos']

    for subject in tqdm(data_et['run_id'].unique(),
                        desc='Adding new x and y position: '):
        df_subj = data_et.loc[data_et['run_id'] == subject]

        for fix_trial in df_subj.loc[
            (df_subj['run_id'] == subject) &
            (df_subj['fixTask'] == 1), 'trial_index'].unique():
            # Get x_pos of current fix dot
            x_pos = data_et.loc[
                (data_et['run_id'] == subject) &
                (data_et['trial_index'] == fix_trial),
                'x_pos'].values[0]

            # Insert x_pos at the previous fix cross
            data_et.loc[
                (data_et['run_id'] == subject) &
                (data_et['trial_index'] == (fix_trial - 1)),
                'new_x_pos'] = x_pos

            # Get y_pos of current fix dot
            y_pos = data_et.loc[
                (data_et['run_id'] == subject) &
                (data_et['trial_index'] == fix_trial),
                'y_pos'].values[0]

            # Insert y_pos at the previous fix cross
            data_et.loc[
                (data_et['run_id'] == subject) &
                (data_et['trial_index'] == (fix_trial - 1)),
                'new_y_pos'] = y_pos

            # Same for position Index
            # Get y_pos of current fix dot
            positionIndex = data_et.loc[
                (data_et['run_id'] == subject) &
                (data_et['trial_index'] == fix_trial),
                'positionIndex'].values[0]

            # Insert y_pos at the previous fix cross
            data_et.loc[
                (data_et['run_id'] == subject) &
                (data_et['trial_index'] == (fix_trial - 1)),
                'positionIndex'] = positionIndex

    summary = data_et.groupby(
        ['run_id', 'trial_index', 'fixTask', 'trial_duration'],
        as_index=False)[[
            'new_x_pos', 'new_y_pos']].mean()

    print(
        f"""Assigned new x and y positions: \n"""
        f"""{summary.head(10)} \n"""
    )

    return data_et


def new_position_index(data_et):
    for subject in tqdm(data_et['run_id'].unique(),
                        desc='new Position Index: '):
        df_subj = data_et.loc[data_et['run_id'] == subject]

        for fix_trial in df_subj.loc[
            (df_subj['run_id'] == subject) &
            (df_subj['fixTask'] == 0), 'trial_index'].unique():

            # Same for position Index
            position_index = data_et.loc[
                (data_et['run_id'] == subject) &
                (data_et['trial_index'] == (fix_trial + 1)),
                'positionIndex'].values[0]

            data_et.loc[
                (data_et['run_id'] == subject) &
                (data_et['trial_index'] == fix_trial),
                'positionIndex'] = position_index

    summary = data_et.groupby(
        ['run_id', 'trial_index', 'fixTask', 'trial_duration'],
        as_index=False)[[
            'new_x_pos', 'new_y_pos', 'positionIndex']].mean()

    print(
        f"""Changed position index: \n"""
        f"""{summary.head(10)} \n"""
    )

    return data_et


def euclidean_distance(x, x_target, y, y_target):
    x_diff = x - x_target
    y_diff = y - y_target

    return np.sqrt(x_diff ** 2 + y_diff ** 2)


def create_median_line(data):
    binArray = np.arange(-1500, 5000, 100)
    bins = pd.cut(data['t_task'], binArray)
    output = data.groupby(bins) \
        .agg({"offset": "median"}).reset_index()
    print(output)
    output['t_task'] = binArray[0:len(output)]

    return output


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
            yerr=[data['offset_std_lower'], data[(outcome + '_std_upper')]],
            fmt='^k:',
            capsize=5
        )
    makedir('results', 'plots', 'fix_task')
    plt.savefig(
        os.path.join('results', 'plots', '',
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
    grouped = data_et_fix.groupby(['run_id', 'trial_index']) \
        ['x', 'y'].mean() \
        .reset_index() \
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
    data_trial_fix['x_mean_px'] = data_trial_fix['x_mean'] * data_trial_fix['window_width']
    data_trial_fix['y_mean_px'] = data_trial_fix['y_mean'] * data_trial_fix['window_height']
    data_trial_fix.loc[:, ['x_mean', 'x_mean_px', 'y_mean', 'y_mean_px']].describe()

    # %%

    data_trial_fix['grand_deviation'] = euclidean_distance(
        data_trial_fix['x_mean'], data_trial_fix['x_pos'],
        data_trial_fix['y_mean'], data_trial_fix['y_pos']
    )

    summary = data_trial_fix['grand_deviation'].describe()

    print(
        f"""Grand mean deviation: \n"""
        f"""{summary}""")

    return data_trial_fix


def compare_conditions_subject(data_subject, data_trial_fix, outcome):
    data_subject = separate_outcomes_by_condition(
        data_subject, data_trial_fix, outcome, 'chin')

    data_subject = separate_outcomes_by_condition(
        data_subject, data_trial_fix, outcome, 'glasses_binary')

    summary = data_subject.loc[
              :,
              [
                  outcome, (outcome + '_chin_0'),
                  (outcome + '_chin_1'), (outcome + '_glasses_binary_0'),
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
        .pivot(index='run_id', columns=varCondition, values=varName) \
        .reset_index() \
        .rename(columns={0.0: var_cond_0, 1.0: var_cond_1})
    data = data.merge(grouped.loc[:, ['run_id', var_cond_0, var_cond_1]], on='run_id', how='left')
    return data
