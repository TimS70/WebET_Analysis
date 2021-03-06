import os

import numpy as np
import pandas as pd

from analysis.correlations import clean_corr_data, combine_corr_matrix
from utils.save_data import write_csv
from visualize.all_tasks import save_plot
import seaborn as sns
import matplotlib.pyplot as plt


def corr_analysis_fix(data_trial, data_subject, path_plots, path_tables,
                      trial_analysis=False):

    if trial_analysis:
        corr_columns_trial = ['fps', 'x_pos', 'y_pos',
                              'glasses_binary', 'chin',
                              'precision', 'offset', 'hit_mean']

        corr_columns_trial.sort(reverse=True)

        # Trial level
        data_plot = data_trial[
            np.append(['run_id', 'withinTaskIndex'], corr_columns_trial)]
        data_plot = clean_corr_data(data_plot)

        sns.set()
        sns.pairplot(data=data_plot,
                     vars=['fps', 'precision', 'offset'],
                     hue='chin',
                     kind='reg',
                     corner=True,
                     plot_kws=dict(scatter_kws=dict(s=0.1)))
        save_plot(file_name='scatter_matrix_trial.png',
                  path=path_plots,
                  message=True)
        plt.close()

        matrix, matrix_stars = combine_corr_matrix(data=data_plot,
                                                   variables=corr_columns_trial)

        write_csv(data=matrix,
                  index=True,
                  file_name='corr_matrix_trial.csv',
                  path=path_tables)

    # Participant level

    data_subject['1_hit_ratio'] = data_subject['hit_mean']
    data_subject['2_offset'] = data_subject['offset']
    data_subject['3_precision'] = data_subject['precision']
    data_subject['4_fps'] = data_subject['fps']
    data_subject['5_ethnic'] = data_subject['ethnic']
    data_subject['6_age'] = data_subject['age']
    data_subject['7_glasses'] = data_subject['glasses_binary']
    data_subject['8_window'] = data_subject['window']
    data_subject['9_webcam_resolution'] = data_subject['webcam_diag']

    corr_columns_subject = [
        '1_hit_ratio',
        '2_offset',
        '3_precision',
        '4_fps',
        '5_ethnic',
        '6_age',
        '7_glasses',
        '8_window',
        '9_webcam_resolution']

    corr_columns_subject.sort(reverse=False)

    # Trial level
    data_plot = data_subject[np.append(['run_id'], corr_columns_subject)]
    # data_plot = clean_corr_data(data_plot)

    sns.set()
    sns.pairplot(data=data_plot,
                 vars=corr_columns_subject.remove('5_ethnic'),
                 kind='reg',
                 corner=True,
                 plot_kws=dict(scatter_kws=dict(s=0.5)))
    save_plot(file_name='scatter_matrix_subject.png',
              path=path_plots,
              message=True)
    plt.close()

    matrix, matrix_stars = combine_corr_matrix(data=data_plot,
                                               variables=corr_columns_subject)
    write_csv(data=matrix.reset_index(),
              file_name='corr_matrix_subject.csv',
              path=path_tables)

    matrix_stars['n'] = data_plot[corr_columns_subject].count().values
    matrix_stars['M'] = data_plot[corr_columns_subject].mean().values
    matrix_stars['SD'] = data_plot[corr_columns_subject].std().values
    matrix_stars[['M', 'SD']] = round(matrix_stars[['M', 'SD']], 2)
    matrix_stars = matrix_stars[np.append(['n', 'M', 'SD'],
                                          corr_columns_subject)]

    write_csv(data=matrix_stars,
              file_name='corr_matrix_subject_stars.csv',
              path=path_tables, index=True)
