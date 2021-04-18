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
    data_subject['1 age'] = data_subject['age']
    data_subject['2 fps'] = data_subject['fps']
    data_subject['3 logK'] = data_subject['logK']
    data_subject['4 choseLL'] = data_subject['choseLL']
    data_subject['5 choice_rt'] = data_subject['choice_rt']
    data_subject['6 optionIndex'] = data_subject['optionIndex']
    data_subject['7 attributeIndex'] = data_subject['attributeIndex']
    data_subject['8 payneIndex'] = data_subject['payneIndex']

    corr_columns_subject = ['1 age',
                            '2 fps',
                            '3 logK',
                            '4 choseLL',
                            '5 choice_rt',
                            '6 optionIndex',
                            '7 attributeIndex',
                            '8 payneIndex']

    corr_columns_subject.sort(reverse=False)

    data_plot = data_subject[np.append(['run_id'], corr_columns_subject)]
    data_plot = clean_corr_data(data_plot)

    sns.set()
    sns.pairplot(data=data_plot,
                 vars=corr_columns_subject,
                 kind='reg',
                 corner=True,
                 plot_kws=dict(scatter_kws=dict(s=0.5)))
    save_plot(file_name='scatter_matrix_subject.png',
              path=path_plots,
              message=True)
    plt.close()

    matrix, matrix_stars = combine_corr_matrix(data=data_plot,
                                               variables=corr_columns_subject)

    write_csv(data=matrix,
              file_name='corr_matrix_subject.csv',
              path=path_tables, index=True)

    matrix_stars['n'] = data_plot[corr_columns_subject].count().values
    matrix_stars['M'] = data_plot[corr_columns_subject].mean().values
    matrix_stars['SD'] = data_plot[corr_columns_subject].std().values
    matrix_stars[['M', 'SD']] = round(matrix_stars[['M', 'SD']], 2)
    matrix_stars = matrix_stars[np.append(['n', 'M', 'SD'],
                                          corr_columns_subject)]

    write_csv(data=matrix_stars,
              file_name='corr_matrix_subject_stars.csv',
              path=path_tables, index=True)
