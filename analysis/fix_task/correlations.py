import os

import numpy as np

from data_prep.cleaning.corr_data import clean_corr_data
from visualize.all_tasks import corr_matrix, corr_plot_split, scatter_matrix


def corr_analysis(data_trial, data_subject):

    # Trial level
    data_plot = data_trial[[
        'run_id', 'withinTaskIndex', 'window_diagonal', 'age', 'fps',
        'x_pos', 'y_pos', 'glasses_binary', 'chin',
        'precision', 'offset']]
    data_plot = clean_corr_data(data_plot)

    corr_columns = ['withinTaskIndex', 'fps', 'offset', 'precision']

    scatter_matrix(
        data=data_plot,
        corr_variables=corr_columns,
        file_name='corr_var_vs_chin.png',
        path_target=os.path.join('chin', 'results', 'plots', 'fix_task',
                                 'correlations'))

    corr_columns = np.append(['x_pos', 'y_pos'], corr_columns)

    corr_matrix(data_plot, corr_columns,
                'table_p', 'trial_corr_p.csv',
                'results', 'tables', 'fix_task', 'correlations')
    corr_matrix(data_plot, corr_columns,
                'table_n', 'trial_corr_n.csv',
                'results', 'tables', 'fix_task', 'correlations')