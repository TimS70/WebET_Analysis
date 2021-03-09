import os
import scipy

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statsmodels.stats.multitest as smt

from scipy import stats

from analysis.fix_task.main_effects import t_test_ind_outcomes_vs_factor
from utils.path import makedir
from utils.plots import save_plot
from utils.tables import write_csv


def check_randomization(data_trial_fix):
    plot_chin_first_vs_outcomes(data_trial_fix)
    t_test_ind_outcomes_vs_factor(data_trial_fix, 'chinFirst', '',
                                  'results', 'tables', 'fix_task',
                                  'check_randomization')

    plot_outcomes_by_task_order(data_trial_fix)

    print(f"""Plots show a greater variance in the second run. \n""")

    test_outcomes_by_task_order(data_trial_fix)

    print('Tendency for lower overall precision for those who '
          'started with the chin-rest, not for Holm correction. \n')


# noinspection PyTypeChecker
def plot_chin_first_vs_outcomes(data_trial_fix):
    data_plot = data_trial_fix.groupby(
        ['run_id', 'chinFirst', 'chin'],
        as_index=False)[['offset', 'precision', 'fps']].mean()
    data_plot.head(5)

    # %%

    for outcome in ['offset', 'precision']:
        fig, axes = plt.subplots(
            1, 2, sharey='none', figsize=(15, 6))
        fig.suptitle((outcome + ' chinFirst==0 vs. chinFirst==1'))

        sns.violinplot(ax=axes[0], x='chinFirst', y=outcome,
                       data=data_plot.loc[data_plot['chin'] == 0, :])
        sns.violinplot(ax=axes[1], x='chinFirst', y=outcome,
                       data=data_plot.loc[data_plot['chin'] == 1, :])

        save_plot(('chinFirst_vs_' + outcome),
                  'results', 'plots', 'fix_task', 'check_randomization')
        plt.close()


def plot_outcomes_by_task_order(data_trial_fix):
    outcomes_by_fix_order = data_trial_fix \
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

    makedir('results', 'plots', 'fix_task',
            'check_randomization')
    plt.savefig(
        os.path.join('results', 'plots',
                     'fix_task', 'check_randomization',
                     'outcomes_by_task_order.png'))
    plt.close()


# noinspection DuplicatedCode
def test_outcomes_by_task_order(data_trial_fix):
    outcomes_by_fix_order = data_trial_fix \
        .rename(columns={'task_nr': 'fix_order'}) \
        .groupby(
            ['run_id', 'chin', 'fix_order'],
            as_index=False)[['offset', 'precision', 'fps']] \
        .mean()
    outcomes_by_fix_order['fix_order'] = \
        outcomes_by_fix_order['fix_order'] \
            .replace({3.0: 2.0}) \
            .astype(int)

    outcomes_by_fix_order = outcomes_by_fix_order \
        .pivot(index='run_id',
               columns='fix_order',
               values=['offset', 'precision', 'fps'])

    summary = outcomes_by_fix_order.mean() \
        .reset_index() \
        .rename(columns={'level_0': 'measure', 0: 'mean'}) \
        .assign(SD=outcomes_by_fix_order.std().reset_index(drop=True)) \
        .assign(n=outcomes_by_fix_order.count().reset_index(drop=True))

    result_offset = t_test_rel('offset', outcomes_by_fix_order)
    result_precision = t_test_rel('precision', outcomes_by_fix_order)
    result_fps = t_test_rel('fps', outcomes_by_fix_order)

    chin_test = pd.DataFrame({
        'measure': ['offset', 'precision', 'fps'],
        't': [
            result_offset.statistic,
            result_precision.statistic,
            result_fps.statistic
        ],
        'p': [
            result_offset.pvalue,
            result_precision.pvalue,
            result_fps.pvalue
        ]
    }
    )
    chin_test['t'] = (chin_test['t']).astype(float)
    # Holm correction
    chin_test['p'] = smt.multipletests(chin_test['p'], method='holm')[1].astype(float)

    summary = summary.merge(
        chin_test,
        on='measure',
        how='left'
    )
    print('summary order')
    print(summary)

    write_csv(
        summary,
        't_test_task_order_vs_outcomes.csv',
        'results', 'tables', 'fix_task', 'check_randomization')


def t_test_rel(outcome_var, outcomes_by_fix_order):
    return scipy.stats.ttest_rel(
        outcomes_by_fix_order.loc[:, [(outcome_var, 1)]],
        outcomes_by_fix_order.loc[:, [(outcome_var, 2)]]
    )
