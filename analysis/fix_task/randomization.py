import os
import scipy

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statsmodels.stats.multitest as smt

from scipy import stats

from inference.t_test import t_test_outcomes_vs_factor
from utils.path import makedir
from visualize.all_tasks import save_plot
from utils.save_data import write_csv


def check_randomization(data_trial, path_tables, path_plots):
    plot_chin_first_vs_outcomes(data=data_trial, path_target=path_plots)

    t_test_outcomes_vs_factor(
        data=data_trial,
        factor='chinFirst',
        outcomes=['offset', 'precision', 'fps'],
        dependent=False,
        file_name='t_test_chinFirst_vs_outcomes.csv',
        path=os.path.join(path_tables, 'randomization'))

    plot_outcomes_by_task_order(data=data_trial,
                                file_name='outcomes_by_task_order.png',
                                path_target=path_plots)

    print(f"""Plots show a greater variance in the second run. \n""")

    data_trial['fix_order'] = data_trial['task_nr'] \
        .replace({3.0: 2.0}) \
        .astype(int)

    t_test_outcomes_vs_factor(
        data=data_trial,
        dependent=True,
        factor='fix_order',
        outcomes=['offset', 'precision', 'fps', 'hit_mean'],
        file_name='t_test_chin_vs_outcomes.csv',
        path=os.path.join(path_tables))

    print('Tendency for lower overall precision for those who '
          'started with the chin-rest, not for Holm correction \n')


# noinspection PyTypeChecker
def plot_chin_first_vs_outcomes(data, path_target):
    data_plot = data.groupby(
        ['run_id', 'chinFirst', 'chin'],
        as_index=False)[['offset', 'precision', 'fps']].mean()

    for outcome in ['offset', 'precision']:
        fig, axes = plt.subplots(
            1, 2, sharey='none', figsize=(15, 6))
        fig.suptitle((outcome + ' chinFirst==0 vs. chinFirst==1'))

        sns.violinplot(ax=axes[0], x='chinFirst', y=outcome,
                       data=data_plot.loc[data_plot['chin'] == 0, :])
        sns.violinplot(ax=axes[1], x='chinFirst', y=outcome,
                       data=data_plot.loc[data_plot['chin'] == 1, :])

        save_plot(file_name='chinFirst_vs_' + outcome + 'png',
                  path=path_target)
        plt.close()


def plot_outcomes_by_task_order(data, file_name, path_target):
    outcomes_by_fix_order = data \
        .rename(columns={'task_nr': 'fix_order'}) \
        .groupby(
            ['run_id', 'chin', 'fix_order'],
            as_index=False)[['offset', 'precision', 'fps']] \
        .mean()

    outcomes_by_fix_order['fix_order'] = \
        outcomes_by_fix_order['fix_order'] \
        .replace({3.0: 2.0}) \
        .astype(int)

    fig, axes = plt.subplots(1, 2, sharey='none', figsize=(15, 6))
    fig.suptitle('Offset and precision')

    sns.violinplot(
        ax=axes[0], x='fix_order', y='offset',
        hue='chin', split=True,
        data=outcomes_by_fix_order)
    sns.violinplot(
        ax=axes[1], x='fix_order', y='precision',
        hue='chin', split=True,
        data=outcomes_by_fix_order)

    save_plot(file_name=file_name, path=path_target)
    plt.close()
