import os

import numpy as np
import pandas as pd

from analysis.correlations import clean_corr_data, combine_corr_matrix
from utils.save_data import write_csv
from visualize.all_tasks import save_plot
import seaborn as sns
import matplotlib.pyplot as plt


def corr_analysis_choice(data_trial, data_subject, path_plots, path_tables):

    data_trial['rt'] = data_trial['trial_duration_exact']
    corr_columns_trial = ['choseLL', 'k', 'rt', 'LL_top',
                          'optionIndex', 'attributeIndex', 'payneIndex']

    corr_columns_trial.sort(reverse=True)

    # Trial level
    data_plot = data_trial[
        np.append(['run_id', 'withinTaskIndex'], corr_columns_trial)]
    data_plot = clean_corr_data(data_plot)

    sns.set()
    sns.pairplot(data=data_plot,
                 vars=corr_columns_trial.remove('choseLL'),
                 hue='choseLL',
                 kind='reg',
                 corner=True,
                 plot_kws=dict(scatter_kws=dict(s=0.1)))
    save_plot(file_name='scatter_matrix_trial.png',
              path=path_plots,
              message=True)
    plt.close()

    matrix, matrix_stars = combine_corr_matrix(
        data=data_plot, variables=corr_columns_trial)

    write_csv(data=matrix,
              file_name='corr_matrix_trial.csv',
              path=path_tables,
              index=True)

    # Participant level
    corr_columns_subject = ['age', 'fps', 'logK', 'choseLL', 'choice_rt',
                            'optionIndex', 'attributeIndex', 'payneIndex']

    corr_columns_subject.sort(reverse=True)

    # Trial level
    data_plot = data_subject[np.append(['run_id'], corr_columns_subject)]
    data_plot = clean_corr_data(data_plot)

    sns.set()
    sns.pairplot(data=data_plot,
                 vars=['choseLL', 'choice_rt', 'logK',
                       'attributeIndex', 'optionIndex', 'payneIndex',
                       'fps', 'age'],
                 kind='reg',
                 corner=True,
                 plot_kws=dict(scatter_kws=dict(s=0.5)))
    save_plot(file_name='scatter_matrix_subject.png',
              path=path_plots,
              message=True)
    plt.close()

    matrix, matrix_stars = combine_corr_matrix(data=data_plot,
                                               variables=corr_columns_subject)

    matrix_stars['M'] = data_plot[corr_columns_subject].mean().values
    matrix_stars['SD'] = data_plot[corr_columns_subject].std().values
    matrix_stars[['M', 'SD']] = round(matrix_stars[['M', 'SD']], 2)
    matrix_stars = matrix_stars[np.append(['M', 'SD'], corr_columns_subject)]

    write_csv(data=matrix,
              file_name='corr_matrix_subject.csv',
              path=path_tables, index=True)

    write_csv(data=matrix_stars,
              file_name='corr_matrix_subject_stars.csv',
              path=path_tables, index=True)
