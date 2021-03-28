import os

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np

from visualize.all_tasks import save_plot
from visualize.eye_tracking import my_heatmap


# Correction
# Robert Rosenthal. The hand-book of research synthesis, chapter
# Parametric measures of effect size, pages 231–244.
# New York, NY: Russel Sage Foundation, 1994.
# t / sqrt n


def hist_plots_quality(data_subject):
    font_size = 15
    plt.rcParams.update({'font.size': font_size})

    for outcome in ['offset', 'precision', 'fps']:
        plt.hist(data_subject[outcome], bins=20)
        plt.title(outcome + ' Histogram')
        save_plot(file_name=outcome + '_histogram.png',
                  path=os.path.join('results', 'plots',
                                    'fix_task', outcome))
        plt.close()


def fix_heatmap(data_et_fix):
    for run in data_et_fix['run_id'].unique():

        data = data_et_fix[
            (data_et_fix['run_id'] == run) &
            (data_et_fix['t_task'] > 1000) &
            (data_et_fix['x'] > 0) & (data_et_fix['x'] < 1) &
            (data_et_fix['y'] > 0) & (data_et_fix['y'] < 1)]

        x = data['x']
        y = data['y']

        fig, ax = plt.subplots(figsize=(7, 7))

        s = 34
        img, extent = my_heatmap(x, y, s=s)

        ax.imshow(img, extent=extent, origin='upper', cmap=cm.Greens,
                  aspect=(9 / 16))
        ax.set_xlim(0, 1)
        ax.set_ylim(1, 0)
        ax.set_title(
            "Distribution of fixations after 1 second, $\sigma$ = %d" % s)

        x_pos = [0.2, 0.5, 0.8, 0.2, 0.5, 0.8, 0.2, 0.5, 0.8]
        y_pos = [0.2, 0.2, 0.2, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8]
        for i in range(0, len(x_pos)):
            plt.text(x_pos[i], y_pos[i], '+', size=12, ha="center")

        save_plot(file_name=str(run) + '.png',
                  path=os.path.join(
                      'results', 'plots',
                      'fix_task',
                      'individual_participants', 'heatmaps'))
        plt.close()


# noinspection PyUnboundLocalVariable
def visualize_exemplary_run(data_plot):
    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(18, 12))
    axes = axes.ravel()
    x_pos = [0.2, 0.5, 0.8, 0.2, 0.5, 0.8, 0.2, 0.5, 0.8]
    y_pos = [0.2, 0.2, 0.2, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8]
    for i in range(0, 9):
        axes_data = data_plot.loc[
                    (data_plot['x_pos'] == x_pos[i]) &
                    (data_plot['y_pos'] == y_pos[i]), :]
        image = axes[i].scatter(
            axes_data['x'],
            axes_data['y'],
            c=axes_data['t_task'],
            cmap='viridis'
        )
        axes[i].set_ylim(1, 0)
        axes[i].set_xlim(0, 1)

    fig.colorbar(image, ax=axes)

    run = data_plot['run_id'].unique()[0]
    save_plot(file_name='exemplary_run_' + str(run) +
                        '.png',
              path=os.path.join('results', 'plots',
                                'fix_task',
                                'individual_participants'))
    plt.close()


def plot_hit_means_per_dot(data_trial, min_hit_ratio):
    plt.hist(data_trial['hit_mean'], bins=50)

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
                                'fix_task', 'offset'))
    plt.close()
