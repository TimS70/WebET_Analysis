import os

import matplotlib.pyplot as plt
import seaborn as sns

from analysis.fix_task.positions import outcome_by_position_long
from visualize.all_tasks import save_plot


def plot_top_vs_bottom_positions(data_trial_fix, outcome, path_target):
    outcome_by_y_pos = outcome_by_position_long(
        data_trial_fix, outcome) \
        .groupby(
        ['run_id', 'y_pos'],
        as_index=False)[outcome].mean()
    outcome_by_y_pos = outcome_by_y_pos.loc[
                       outcome_by_y_pos['y_pos'] != 0.5, :]

    fig, axes = plt.subplots(1, 1, sharey='none', figsize=(6, 6))
    fig.suptitle((outcome + ' top vs. bottom '))

    sns.violinplot(ax=axes,
                   x='y_pos',
                   y=outcome,
                   data=outcome_by_y_pos)

    save_plot(file_name=outcome + '_top_vs_bottom.png',
              path=os.path.join(path_target, outcome))
    plt.close()
