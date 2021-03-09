import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from utils.data_frames import merge_by_index
from utils.path import makedir
from utils.tables import write_csv


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
        os.path.join('results', 'plots', 'fix_task', 'saccade',
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
        ['new_x_pos', 'new_y_pos', 'trial_duration'],
        as_index=False)['positionIndex'].mean()

    print(
        f"""Changed position index: \n"""
        f"""{summary.head(5)} \n"""
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
    output['t_task'] = binArray[0:len(output)]

    return output
