import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from utils.combine import merge_by_index
from utils.euclidean import euclidean_distance
from utils.path import makedir
from utils.save_data import write_csv
from visualize.all_tasks import save_plot


def check_gaze_saccade(path_origin, path_target, individual=False):

    data_et = pd.read_csv(os.path.join(path_origin, 'data_et.csv'))
    data_trial = pd.read_csv(os.path.join(path_origin, 'data_trial.csv'))

    data_et = merge_by_index(data_et, data_trial,
                             'task_nr_new', 'chinFirst', 'trial_type',
                             'trial_duration', 'trial_duration_exact',
                             'fixTask', 'x_pos', 'y_pos', 'chin',
                             'window_width', 'window_height')

    data_et = data_et.assign(
        x_px=data_et['x'] * data_et['window_width'],
        y_px=data_et['y'] * data_et['window_height'])

    data_cross_dots = select_fix_cross_and_fix_task(data_et)

    data_cross_dots = add_new_position(data_cross_dots)

    data_cross_dots = shift_t_task_for_fix_cross(data_cross_dots)

    data_cross_dots = data_cross_dots.assign(
        offset=euclidean_distance(
            data_cross_dots['x'], data_cross_dots['new_x_pos'],
            data_cross_dots['y'], data_cross_dots['new_y_pos']),
        offset_px=euclidean_distance(
            data_cross_dots['x_px'],
            data_cross_dots['new_x_pos'] * data_cross_dots['window_width'],
            data_cross_dots['y_px'],
            data_cross_dots['new_y_pos'] * data_cross_dots['window_height']))

    if individual:
        print(f"""Plot individual saccades for """
              f"""n={len(data_cross_dots['run_id'].unique())} """
              f"""runs """)
        for run in data_cross_dots['run_id'].unique():
            plot_gaze_saccade(
                data=data_cross_dots[data_cross_dots['run_id'] == run],
                file_name=str(round(run)) + '.png',
                path=path_target)
    else:
        plot_gaze_saccade_by_position(data=data_cross_dots,
                                      file_name='saccades_all.png',
                                      path=path_target)


def plot_gaze_saccade(data, file_name, path):
    average_line_no_chin = create_bin_line(data[data['chin'] == 0])
    average_line_chin = create_bin_line(data[data['chin'] == 1])

    # noinspection PyTypeChecker
    fig, axes = plt.subplots(
        nrows=1, ncols=2, sharey=True, figsize=(18, 12))
    fig.suptitle(
        'Median local offset for all subjects across a '
        'fixation task trial', fontsize=20)

    axes[0].set_title("Chin==0")
    axes[1].set_title("Chin==1")

    sns.scatterplot(ax=axes[0],
                    data=data.loc[
                         data['chin'] == 0, :],
                    x="t_task",
                    y="offset")

    sns.lineplot(ax=axes[0],
                 x=average_line_no_chin['t_task'],
                 y=average_line_no_chin['offset'],
                 color='r')

    sns.scatterplot(ax=axes[1],
                    data=data.loc[
                         data['chin'] == 1, :],
                    x="t_task",
                    y="offset")

    sns.lineplot(ax=axes[1],
                 x=average_line_chin['t_task'],
                 y=average_line_chin['offset'],
                 color='r')

    plt.setp(axes, xlim=(-1500, 5000), ylim=(1, 0))
    plt.xlabel("t_task")

    save_plot(file_name=file_name, path=path, message=True)
    plt.close()


def plot_gaze_saccade_by_position(data, file_name, path):

    # noinspection PyTypeChecker
    fig, axes = plt.subplots(nrows=1, ncols=1, sharey=True, figsize=(7, 7))

    sns.scatterplot(ax=axes, data=data,
                    x="t_task", y="offset",
                    s=0.5)

    xy_positions = [(0.2, 0.2),
                    (0.5, 0.2),
                    (0.8, 0.2),
                    (0.2, 0.5),
                    (0.5, 0.5),
                    (0.8, 0.5),
                    (0.2, 0.8),
                    (0.5, 0.8),
                    (0.8, 0.8)]

    summary = []

    # Get list into an iterable number
    # (x, y) are the parameters ('rows') of the tuple
    for i, (x, y) in enumerate(xy_positions):
        data_this_pos = data[(data['new_x_pos'] == x) &
                             (data['new_y_pos'] == y)]

        median_line = create_bin_line(data_this_pos)

        summary.append([
            x,
            y,
            median_line.loc[median_line['t_task'] < 0, 'offset'].mean(),
            median_line.loc[median_line['t_task'] > 1000, 'offset'].mean(),
            median_line.loc[median_line['t_task'] < 0, 'offset_px'].mean(),
            median_line.loc[median_line['t_task'] > 1000, 'offset_px'].mean()
        ])

        sns.lineplot(ax=axes,
                     x=median_line['t_task'],
                     y=median_line['offset'],
                     legend='brief',
                     label='x=' + str(x) + ', y=' + str(y))

        axes.set_yticks(np.arange(0, 1.2, 0.2), minor=False)
        axes.set_yticks(np.arange(0, 1, 0.1), minor=True)
        axes.grid(axis='y', which='major', alpha=0.5)
        axes.grid(axis='y', which='minor', alpha=0.2)
        axes.grid(axis='x', which='major', alpha=0.5)

    summary = pd.DataFrame(summary,
                           columns=['x_pos', 'y_pos',
                                    'cross_offset',
                                    'stimulus_offset',
                                    'cross_offset_px',
                                    'stimulus_offset_px'])

    describe_summary = summary.loc[
        (summary['x_pos'] != 0.5) & (summary['y_pos'] != 0.5),
        ['cross_offset', 'cross_offset_px',
         'stimulus_offset', 'stimulus_offset_px']].describe()

    describe_summary[['cross_offset', 'stimulus_offset']] = 100 * round(
        describe_summary[['cross_offset', 'stimulus_offset']], 4)

    describe_summary[['cross_offset_px', 'stimulus_offset_px']] = round(
        describe_summary[['cross_offset_px', 'stimulus_offset_px']], 2)

    print(f"""Summarizing median lines: \n"""
          f"""{summary} \n\n"""
          f"""Describe all except the center stimulus: \n"""
          f"""{round(describe_summary, 2)} \n""")

    write_csv(
        data=round(summary, 2),
        file_name='saccade_positions.csv',
        path=os.path.join('results', 'tables', 'fix_task'),
        index=False
    )

    write_csv(
        data=round(describe_summary, 2),
        file_name='saccade_positions_summary.csv',
        path=os.path.join('results', 'tables', 'fix_task'),
        index=True
    )

    plt.setp(axes, xlim=(-1600, 5100), ylim=(0, 1))

    plt.legend(loc='upper right', bbox_to_anchor=[0.95, 1])
    plt.xlabel('time [ms]')
    plt.ylabel('distance to target [% screen size]')
    fig.suptitle('Offset', fontsize=14)

    plt.vlines(x=-1500, ymin=0, ymax=1, colors='k', linestyles='solid')
    plt.text(x=-1400, y=0.9, s='Fixation Cross \nonset')
    plt.vlines(x=0, ymin=0, ymax=1, colors='k', linestyles='solid')
    plt.text(x=100, y=0.9, s='Stimulus \nonset')
    plt.vlines(x=5000, ymin=0, ymax=1, colors='k', linestyles='solid')
    plt.text(x=4100, y=0.5, s='Stimulus \noffset')

    save_plot(file_name=file_name, path=path, message=True)
    plt.close()


def select_fix_cross_and_fix_task(data):
    data_cross_and_task = data[
                          (data['trial_type'] == 'eyetracking-fix_object') &
                          (
                                  (data['chinFirst'] == 0) &
                                  (data['task_nr_new'].isin([1, 2]))
                          ) |
                          (
                                  (data['chinFirst'] == 1) &
                                  (data['task_nr_new'].isin([1, 3]))
                          )].reset_index(drop=True)

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


def add_new_position(data_et):
    data_new_pos = create_new_pos_datasets(data_et)
    data_et = merge_by_index(data_et, data_new_pos,
                             'new_x_pos', 'new_y_pos')

    print('Added new position variables. \n')

    return data_et


def create_new_pos_datasets(data_et_fix):
    data_trial = data_et_fix[['run_id', 'trial_index', 'trial_duration',
                              'x_pos', 'y_pos']] \
        .drop_duplicates() \
        .reset_index() \

    data_trial['new_x_pos'] = data_trial['x_pos']
    data_trial['new_y_pos'] = data_trial['y_pos']

    for subject in tqdm(data_trial['run_id'].unique(),
                        desc='Create new positions'):

        df_subject = data_trial.loc[data_trial['run_id'] == subject]

        for i in df_subject.index[:-1]:

            cross_trial = (data_trial.loc[i, 'trial_duration'] == 1500) & \
                          (data_trial.loc[i + 1, 'trial_duration'] == 5000)

            if cross_trial:
                data_trial.loc[i, 'new_x_pos'] = data_trial.loc[i + 1, 'x_pos']
                data_trial.loc[i, 'new_y_pos'] = data_trial.loc[i + 1, 'y_pos']

    data_trial = data_trial[['run_id', 'trial_index',
                             'new_x_pos', 'new_y_pos']]

    return data_trial


def create_bin_line(data):
    bin_array = np.arange(-1500, 5000, 100)
    bins = pd.cut(data['t_task'], bin_array)
    output = data \
        .groupby(bins, as_index=False) \
        .agg(offset=("offset", "median"),
             offset_px=("offset_px", "median"))
    output['t_task'] = bin_array[0:len(output)]

    return output
