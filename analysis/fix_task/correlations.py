import numpy as np

from data_prep.cleaning.corr_data import clean_corr_data
from visualize.all_tasks import corr_matrix, corr_plot_split


def corr_analysis(data_trial_fix, data_subject):

    data_plot = data_trial_fix.merge(
        data_subject.loc[:, ['run_id', 'age']], on='run_id', how='left') \
        .loc[:, [
            'run_id', 'chin', 'x_pos', 'y_pos',
            'withinTaskIndex', 'age', 'fps',
            'offset', 'precision']]

    data_plot = clean_corr_data(data_plot)

    corr_columns = ['withinTaskIndex', 'age', 'fps', 'offset', 'precision']
    corr_plot_split(data_plot, corr_columns,
              'corr_var_vs_chin.png', 'chin',
              'results', 'plots', 'fix_task', 'correlations')

    corr_columns = np.append(['x_pos', 'y_pos'], corr_columns)

    corr_matrix(data_plot, corr_columns,
                'table_p', 'trial_corr_p.csv',
                'results', 'tables', 'fix_task', 'correlations')
    corr_matrix(data_plot, corr_columns,
                'table_n', 'trial_corr_n.csv',
                'results', 'tables', 'fix_task', 'correlations')
    corr_matrix(data_plot, corr_columns,
                'heatmap', 'trial_corr_heatmap.png',
                'results', 'plots', 'fix_task', 'correlations')
