import os

import numpy as np
import pandas as pd

from analysis.correlations import clean_corr_data, combine_corr_matrix
from utils.save_data import write_csv
from visualize.all_tasks import save_plot
import seaborn as sns
import matplotlib.pyplot as plt


def corr_analysis_fix(data_trial, data_subject,
                      path_plots, path_tables):

    corr_columns_trial = ['fps', 'x_pos', 'y_pos',
                          'glasses_binary', 'chin',
                          'precision', 'offset']

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

    matrix = combine_corr_matrix(data=data_plot, variables=corr_columns_trial)
    write_csv(data=matrix,
              index=True,
              file_name='corr_matrix_trial.csv',
              path=path_tables)

    # Participant level
    corr_columns_subject = ['glasses_binary', 'window', 'fps',
                            'age', 'ethnic', 'offset', 'precision']

    corr_columns_subject.sort(reverse=True)

    # Trial level
    data_plot = data_subject[np.append(['run_id'], corr_columns_subject)]
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

    matrix = combine_corr_matrix(data=data_plot, variables=corr_columns_subject)
    write_csv(data=matrix.reset_index(),
              file_name='corr_matrix_subject.csv',
              path=path_tables)
