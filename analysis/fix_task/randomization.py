import os

import matplotlib.pyplot as plt
import seaborn as sns

from inference.F import compare_variances
from inference.t_test import t_test_outcomes_vs_factor
from visualize.all_tasks import save_plot
from visualize.fix_task.main import split_violin_plots_outcomes


def check_randomization(data_trial, path_tables, path_plots):
    print('\nChecking randomization \n')
    plot_chin_first_vs_outcomes(data=data_trial, path_target=path_plots)

    t_test_outcomes_vs_factor(
        data=data_trial,
        factor='chinFirst',
        outcomes=['offset', 'precision', 'fps'],
        dependent=False,
        file_name='t_test_chinFirst_vs_outcomes.csv',
        path=os.path.join(path_tables, 'randomization'))

    print(f"""Plots show a greater variance in the second run. \n""")

    data_trial['fix_order'] = data_trial['task_nr'] \
        .replace({3.0: 2.0}) \
        .astype(int)

    split_violin_plots_outcomes(data=data_trial,
                                split_factor='chin',
                                factor='fix_order',
                                file_name='outcomes_by_task_order.png',
                                path_target=path_plots)

    compare_variances(data=data_trial,
                      factor='fix_order',
                      outcome=['offset', 'precision'])

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

        save_plot(file_name='chinFirst_vs_' + outcome + '.png',
                  path=path_target)
        plt.close()
