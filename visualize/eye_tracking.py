import os

import matplotlib.pyplot as plt
import numpy as np

from scipy.ndimage import gaussian_filter

from utils.combine_frames import merge_mean_by_subject
from visualize.all_tasks import save_plot
from visualize.distributions import plot_histogram, plot_2d_histogram


def plot_et_scatter(x, y, c=None,
                    title='Scatter plot of eye-tracking coordinates',
                    label='xy clusters',
                    file_name='et_scatter.png',
                    path='results',
                    message=False):
    """

    :type file_name: Name of file
    """
    plt.scatter(x, y, c=c, s=0.5, label=label)

    plt.xlim(0, 1)
    plt.ylim(1, 0)
    plt.xticks(np.arange(0, 1, 0.1))
    plt.yticks(np.arange(0, 1, 0.1))

    plt.legend(loc='upper right')
    plt.xlabel('X [%]')
    plt.ylabel('Y [%]')
    plt.grid()
    plt.tight_layout()
    plt.box(False)
    plt.title(title)

    save_plot(file_name, path, message)
    plt.close()


def plot_grand_mean(data_subject, data_et):

    plot_histogram(
        data_subject['x_bias'],
        'x_bias_trial_mean.png',
        os.path.join('results', 'plots', 'fix_task', 'offset',
                     'grand_mean'))

    plot_histogram(
        data_subject['y_bias'],
        'y_bias_trial_mean.png',
        os.path.join('results', 'plots', 'fix_task', 'offset',
                     'grand_mean'))

    plot_2d_histogram(
        data_subject['x_bias'], data_subject['y_bias'],
        'xy_bias_trial_mean_2d.png',
        os.path.join('results', 'plots', 'fix_task', 'offset',
                     'grand_mean'))

    # Regardless of trials
    data_subject = merge_mean_by_subject(
        data_subject, data_et, 'x', 'y')

    plot_histogram(
        data_subject['x'],
        'x_bias_no_trials.png',
        os.path.join('results', 'plots', 'fix_task', 'offset',
                     'grand_mean'))

    plot_histogram(
        data_subject['y'],
        'y_bias_no_trials.png',
        os.path.join('results', 'plots', 'fix_task', 'offset',
                     'grand_mean'))

    plot_2d_histogram(
        data_subject['x'], data_subject['y'],
        'xy_bias_no_trials_2d.png',
        os.path.join('results', 'plots', 'fix_task', 'offset',
                     'grand_mean'))


def my_heatmap(x, y, s, bins=[np.arange(0, 1, 0.001),
                              np.arange(0, 1, 0.002)]):
    heatmap, x_edges, y_edges = np.histogram2d(x, y, bins=bins)
    heatmap = gaussian_filter(heatmap, sigma=s)
    extent = [x_edges[0], x_edges[-1], y_edges[-1], y_edges[0]]
    return heatmap.T, extent