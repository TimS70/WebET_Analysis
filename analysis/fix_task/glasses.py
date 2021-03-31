import os

import pandas as pd

from analysis.fix_task.sight import plot_sight_vs_outcomes
from inference.F import anova_outcomes_factor
from inference.t_test import t_test_outcomes_vs_factor
from utils.save_data import write_csv
from visualize.all_tasks import split_violin_plot


def test_glasses(data_trial, data_subject, path_plots, path_tables):
    for var in ['glasses', 'sight', 'glasses_binary']:
        freq_table = pd.crosstab(index=data_subject[var], columns="count")
        print(f"""{freq_table} \n""")
        write_csv(freq_table,
                  'glasses_freq_table_' + var + '.csv',
                  os.path.join(path_plots, 'glasses'))

    plot_sight_vs_outcomes(data=data_subject, path=path_plots)
    anova_outcomes_factor(data=data_subject,
                          factor='sight',
                          path=path_tables)
    anova_outcomes_factor(data=data_subject,
                          factor='glasses',
                          path=path_tables)

    t_test_outcomes_vs_factor(
        data=data_subject,
        factor='glasses_binary',
        dependent=False,
        outcomes=['offset', 'precision', 'fps', 'hit_ratio'],
        file_name='t_test_chin_vs_outcomes.csv',
        path=path_tables)

    for outcome in ['offset', 'precision', 'fps', 'hit_mean']:
        split_violin_plot(
            data_trial=data_trial,
            outcome=outcome,
            factor='chin', split_factor='glasses_binary',
            file_name='split_violin_chin_vs_' + outcome + '_vs_glasses.png',
            path=path_plots)

    print('Check only those with high fps (Semmelmann & Weigelt, 2019)')
    data_t_test = data_subject[data_subject['fps'] > 15]

    if len(data_t_test['glasses_binary'].unique()) > 1:
        t_test_outcomes_vs_factor(
            data=data_subject[
                data_subject['fps'] > data_subject['fps'].median()],
            factor='glasses_binary',
            dependent=False,
            outcomes=['offset', 'precision', 'fps', 'hit_ratio'],
            file_name='t_test_chin_vs_outcomes_high_fps.csv',
            path=path_tables)
