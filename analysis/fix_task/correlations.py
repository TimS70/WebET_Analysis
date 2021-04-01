import os

import numpy as np
import pandas as pd
from data_prep.cleaning.corr_data import clean_corr_data
from utils.combine import merge_by_subject
from utils.save_data import write_csv
from visualize.all_tasks import save_plot
import seaborn as sns
import matplotlib.pyplot as plt


def corr_analysis(data_trial, data_subject, path_plots, path_tables):

    corr_columns = ['window_diagonal', 'fps', 'x_pos', 'y_pos',
                    'glasses_binary', 'chin', 'precision', 'offset']
    corr_columns.sort(reverse=True)

    # Trial level
    data_plot = data_trial[
        np.append(['run_id', 'withinTaskIndex'], corr_columns)]
    data_plot = clean_corr_data(data_plot)

    sns.set()
    sns.pairplot(data=data_plot,
                 vars=['window_diagonal', 'fps', 'precision', 'offset'],
                 hue='chin',
                 kind='reg',
                 corner=True,
                 plot_kws=dict(scatter_kws=dict(s=0.1)))
    save_plot(file_name='scatter_matrix_trial.png',
              path=path_plots,
              message=True)
    plt.close()

    matrix = combine_corr_matrix(data=data_plot, variables=corr_columns)
    write_csv(data_frame=matrix.reset_index(),
              file_name='corr_matrix_trial.csv',
              path=path_tables)

    # Participant level
    grouped = data_trial \
        .groupby(['run_id'], as_index=False) \
        .agg(window=('window_diagonal', 'max'))
    data_subject = merge_by_subject(data_subject, grouped, 'window')

    corr_columns = ['glasses_binary', 'window', 'fps',
                    'age', 'ethnic', 'offset', 'precision']
    corr_columns.sort(reverse=True)

    # Trial level
    data_plot = data_subject[np.append(['run_id'], corr_columns)]
    # data_plot = clean_corr_data(data_plot)

    sns.set()
    sns.pairplot(data=data_plot,
                 vars=['window', 'fps', 'age', 'offset', 'precision'],
                 kind='reg',
                 corner=True,
                 plot_kws=dict(scatter_kws=dict(s=0.5)))
    save_plot(file_name='scatter_matrix_subject.png',
              path=path_plots,
              message=True)
    plt.close()

    matrix = combine_corr_matrix(data=data_plot, variables=corr_columns)
    write_csv(data_frame=matrix.reset_index(),
              file_name='corr_matrix_subject.csv',
              path=path_tables)


def combine_corr_matrix(data, variables):
    matrix_r = data[variables].rcorr(decimals=3, upper='n')
    matrix_r.index = matrix_r.index + '_r'

    matrix_p = data[variables].rcorr(decimals=3, upper='pval', stars=False)
    matrix_p.index = matrix_p.index + '_p'

    matrix_stars = data[variables].rcorr(decimals=3, upper='pval', stars=True)
    matrix_stars.index = matrix_stars.index + '_stars'


    matrix = pd.concat([matrix_r, matrix_p, matrix_stars]) \
        .sort_index(ascending=False)

    return matrix
