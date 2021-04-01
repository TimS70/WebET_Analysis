import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils.combine import merge_by_index, merge_by_subject
from utils.euclidean import euclidean_distance
from visualize.all_tasks import save_plot
from utils.save_data import write_csv, load_all_three_datasets


def grand_mean_offset(path_origin, path_plots, path_tables):
    data_et, data_trial, data_subject = load_all_three_datasets(path_origin)

    grouped = data_et \
        .groupby(['run_id'], as_index=False) \
        .agg(x_mean=('x', 'mean'),
             y_mean=('y', 'mean'))

    data_subject = merge_by_subject(data_subject, grouped, 'x_mean', 'y_mean')

    data_subject = data_subject.assign(
        x_mean_px=data_subject['x_mean'] * data_subject['window_x'],
        y_mean_px=data_subject['y_mean'] * data_subject['window_y'])

    data_subject = data_subject.assign(
        grand_offset=euclidean_distance(data_subject['x_mean'], 0.5,
                                        data_subject['y_mean'], 0.5),
        grand_offset_px=euclidean_distance(
            data_subject['x_mean_px'], data_subject['window_x'] / 2,
            data_subject['y_mean_px'], data_subject['window_y'] / 2))

    summary = data_subject[['x_mean', 'y_mean',
                            'grand_offset', 'grand_offset_px']].describe()

    print(f"""Grand mean offset: \n"""
          f"""{summary} \n""")
    exit()
    # Positions
    grouped = data_et \
        .groupby(['run_id', 'trial_index'], as_index=False) \
        .agg(x_mean=('x', 'mean'),
             y_mean=('y', 'mean'))

    data_trial = merge_by_index(data_trial, grouped, 'x_mean', 'y_mean')

    data_trial = data_trial.assign(
        x_mean_px=data_trial['x_mean'] * data_trial['window_width'],
        y_mean_px=data_trial['y_mean'] * data_trial['window_height'],
        grand_deviation=euclidean_distance(
            data_trial['x_mean'], data_trial['x_pos'],
            data_trial['y_mean'], data_trial['y_pos']))

    data_trial = data_trial.assign(
        grand_deviation_px=euclidean_distance(
            data_trial['x_mean_px'], data_trial['x_pos'],
            data_trial['y_mean_px'], data_trial['y_pos']))

    grand_mean_positions = data_trial \
        .groupby(['x_pos', 'y_pos'], as_index=False) \
        .agg(x_mean=('x_mean', 'mean'),
             y_mean=('y_mean', 'mean'),
             M=('grand_deviation', 'mean'),
             SD=('grand_deviation', 'std'),
             M_px=('grand_deviation_px', 'mean'),
             SD_px=('grand_deviation_px', 'std'))

    print(f"""Grand mean positions: \n"""
          f"""{grand_mean_positions} \n""")

    write_csv(data=grand_mean_positions,
              file_name='grand_mean_positions.csv',
              path=path_tables)

    font_size = 15
    plt.rcParams.update({'font.size': font_size})

    plt.hist(data_trial['grand_deviation'], bins=20)
    plt.title('Grand mean deviation')
    save_plot(file_name='grand_mean.png',
              path=os.path.join(path_plots, 'offset'))
    plt.close()


