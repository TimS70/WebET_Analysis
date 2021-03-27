import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from utils.combine_frames import merge_by_index
from utils.path import makedir


def check_gaze_saccade():

    data_et = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_et.csv'))

    data_trial = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_trial.csv'))

    data_et = merge_by_index(
        data_et, data_trial,
        'task_nr_new', 'chinFirst',
        'trial_duration', 'trial_duration_exact',
        'fixTask')

    data_et_cross_and_task = select_fix_cross_and_fix_task(data_et)

    data_et_cross_and_task = shift_t_task_for_fix_cross(
        data_et_cross_and_task)

    data_et_cross_and_task['offset'] = euclidean_distance(
        data_et_cross_and_task['x'],
        data_et_cross_and_task['new_x_pos'],
        data_et_cross_and_task['y'],
        data_et_cross_and_task['new_y_pos']
    )

    plot_gaze_saccade(
        data_et_cross_and_task,
        ('offset_all_gaze_shift.png'))

    # for subject in tqdm(
    #         data_et_cross_and_task['run_id'].unique(),
    #         desc='Plotting fix task saccade: '):
    #     plot_gaze_saccade(
    #         data_et_cross_and_task.loc[
    #             data_et_cross_and_task['run_id'] == subject, :],
    #         ('offset' + str(subject) + '_gaze_shift.png'))


def plot_gaze_saccade(data_et_cross_and_task, file_name):
    average_line_no_chin = create_median_line(
        data_et_cross_and_task.loc[
            data_et_cross_and_task['chin'] == 0, :])

    average_line_chin = create_median_line(
        data_et_cross_and_task.loc[
            data_et_cross_and_task['chin'] == 1, :])

    # noinspection PyTypeChecker
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


def select_fix_dot_and_cross(data):
    return data.loc[
           (data['trial_type'] == 'eyetracking-fix-object') &
           ((data['task_nr'] == 1) |
            ((data['chinFirst'] == 0) & (data['task_nr'] == 2)) |
            ((data['chinFirst'] == 1) & (data['task_nr'] == 3))
            ), :].reset_index(drop=True)


def shift_t_task_for_fix_cross(data):
    data.loc[
        (data['trial_type'] == 'eyetracking-fix-object') &
        (data['trial_duration'] == 1500),
        't_task'
    ] = data.loc[
            (data['trial_type'] == 'eyetracking-fix-object') &
            (data['trial_duration'] == 1500),
            't_task'] - 1500

    print('Shifted t_task for fixation cross. \n')

    return data


def euclidean_distance(x, x_target, y, y_target):
    x_diff = x - x_target
    y_diff = y - y_target

    return np.sqrt(x_diff ** 2 + y_diff ** 2)


def create_median_line(data):
    bin_array = np.arange(-1500, 5000, 100)
    bins = pd.cut(data['t_task'], bin_array)
    output = data.groupby(bins) \
        .agg({"offset": "median"}).reset_index()
    output['t_task'] = bin_array[0:len(output)]

    return output
