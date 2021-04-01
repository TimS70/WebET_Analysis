import os

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from analysis.fix_task.data_quality import group_within_task_index
from visualize.all_tasks import save_plot
from visualize.eye_tracking import my_heatmap

from tqdm import tqdm

# Correction
# Robert Rosenthal. The hand-book of research synthesis, chapter
# Parametric measures of effect size, pages 231–244.
# New York, NY: Russel Sage Foundation, 1994.
# t / sqrt n


def hist_plots_quality(data_subject, path_plots):
    font_size = 15
    plt.rcParams.update({'font.size': font_size})

    for outcome in ['offset', 'precision', 'fps']:
        plt.hist(data_subject[outcome], bins=20)
        plt.title(outcome + ' Histogram')
        save_plot(file_name=outcome + '_histogram.png',
                  path=os.path.join(path_plots, outcome),
                  message=True)
        plt.close()


def fix_heatmaps(data, path_target):

    data = data[(data['t_task'] > 1000) &
                (data['x'] > 0) & (data['x'] < 1) &
                (data['y'] > 0) & (data['y'] < 1)]

    for run in tqdm(data['run_id'].unique(),
                    desc='Plot fix task heatmaps: '):

        data_this = data[data['run_id'] == run]
        x = data_this['x']
        y = data_this['y']

        fig, ax = plt.subplots(figsize=(7, 7 * (9/16)))

        s = 34
        img, extent = my_heatmap(x, y, s=s)

        ax.imshow(img, extent=extent, origin='upper',
                  cmap=cm.Greens,  aspect=(9 / 16))
        ax.set_xlim(0, 1)
        ax.set_ylim(1, 0)
        ax.set_title('Fix task heatmap for run #' + str(round(run)))
        ax.text(0.0, 1.15,
                f'Distribution of gaze points after 1 second, $\sigma$ = {s}')
        plt.gcf().subplots_adjust(bottom=0.15)

        x_pos = [0.2, 0.5, 0.8, 0.2, 0.5, 0.8, 0.2, 0.5, 0.8]
        y_pos = [0.2, 0.2, 0.2, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8]
        for i in range(0, len(x_pos)):
            plt.text(x_pos[i], y_pos[i], '+', size=12, ha="center")

        save_plot(file_name=str(round(run)) + '.png',
                  path=path_target)
        plt.close()


# noinspection PyUnboundLocalVariable
def visualize_exemplary_run(data, path_target):
    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(18, 12))
    axes = axes.ravel()
    x_pos = [0.2, 0.5, 0.8, 0.2, 0.5, 0.8, 0.2, 0.5, 0.8]
    y_pos = [0.2, 0.2, 0.2, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8]
    for i in range(0, 9):
        axes_data = data.loc[
                    (data['x_pos'] == x_pos[i]) &
                    (data['y_pos'] == y_pos[i]), :]
        image = axes[i].scatter(
            axes_data['x'],
            axes_data['y'],
            c=axes_data['t_task'],
            cmap='viridis'
        )
        axes[i].set_ylim(1, 0)
        axes[i].set_xlim(0, 1)

    fig.colorbar(image, ax=axes)

    run = data['run_id'].unique()[0]
    save_plot(file_name='exemplary_run_' + str(round(run)) +
                        '.png',
              path=path_target,
              message=True)
    plt.close()


def plot_hit_means_per_dot(data_trial, min_hit_ratio):
    plt.hist(data_trial['hit_mean'], bins=50, label='bins=50')

    plt.xticks(np.arange(0, 1, 0.1))

    plt.legend()
    plt.xlabel(f"""Number of gaze points within """
               f"""{round(min_hit_ratio * 100)}% range of the dot [%]""")
    plt.ylabel('Frequency')
    plt.grid()
    plt.tight_layout()
    plt.box(False)
    plt.title('Hits per dot histogram')

    save_plot(file_name='prop_hits_per_dot.png',
              path=os.path.join('results', 'plots',
                                'fix_task', 'offset'),
              message=True)
    plt.close()


def split_violin_plots_outcomes(data, split_factor, factor, file_name,
                                path_target):
    outcomes_by_fix_order = data \
        .groupby(['run_id', split_factor, factor], as_index=False) \
        [['offset', 'precision', 'fps']].mean()

    fig, axes = plt.subplots(1, 2, sharey='none', figsize=(15, 6))
    fig.suptitle('Offset and precision')

    sns.violinplot(
        ax=axes[0], x=factor, y='offset',
        hue=split_factor, split=True,
        data=outcomes_by_fix_order)
    sns.violinplot(
        ax=axes[1], x=factor, y='precision',
        hue=split_factor, split=True,
        data=outcomes_by_fix_order)

    save_plot(file_name=file_name, path=path_target)
    plt.close()


def plot_outcome_over_trials(data_trial, outcome, path_target):
    data_plot = data_trial.copy()

    data_plot['task_nr'] = data_plot['task_nr'] \
        .replace([1, 2, 3], [0, 1, 1])

    data_plot = group_within_task_index(
        data_plot[data_plot['fixTask'] == 1], 'task_nr', outcome)

    plt.style.use('seaborn-whitegrid')
    fig, ax = plt.subplots(1, 2, sharey=True, figsize=(15, 6))
    fig.suptitle('Task 1 vs. Task 2')

    ax[0].set_ylim(0, 1)

    for i in [0, 1]:
        data = data_plot.loc[data_plot['task_nr'] == i, :]
        ax[i].errorbar(
            x=data['withinTaskIndex'],
            y=data[(outcome + '_median')],
            yerr=[data[(outcome + '_std_lower')],
                  data[(outcome + '_std_upper')]],
            fmt='^k:',
            capsize=5)

    save_plot(file_name=outcome + '_vs_trials.png',
              path=os.path.join(path_target, outcome),
              message=True)
    plt.close()


def plot_outcome_over_trials_vs_chin(data_trial, outcome, path_target):
    data_plot = group_within_task_index(
        data_trial[data_trial['fixTask'] == 1], 'chin', outcome)

    plt.style.use('seaborn-whitegrid')
    fig, ax = plt.subplots(1, 2, sharey=True, figsize=(15, 6))
    fig.suptitle('chin==0 vs. chin==1')

    ax[0].set_ylim(0, 1)

    for i in [0, 1]:
        data = data_plot.loc[data_plot['chin'] == i, :]
        ax[i].errorbar(
            x=data['withinTaskIndex'],
            y=data[(outcome + '_median')],
            yerr=[data[(outcome + '_std_lower')],
                  data[(outcome + '_std_upper')]],
            fmt='^k:',
            capsize=5)

    save_plot(file_name=outcome + '_vs_chin_vs_trials.png',
              path=os.path.join(path_target, outcome),
              message=True)
    plt.close()