import os

import numpy as np
from scipy.ndimage import gaussian_filter

from utils.combine_frames import merge_mean_by_subject
from visualize.distributions import plot_histogram, plot_2d_histogram


def plot_xy(data_subject, data_et):

    data_subject = merge_mean_by_subject(
        data_subject, data_et, 'x', 'y')

    plot_histogram(
        data_subject['x'],
        'x.png',
        os.path.join('results', 'plots', 'fix_task', 'offset'))

    plot_histogram(
        data_subject['y'],
        'y.png',
        os.path.join('results', 'plots', 'fix_task', 'offset'))

    plot_2d_histogram(
        data_subject['x'], data_subject['y'],
        'xy_2d.png',
        os.path.join('results', 'plots', 'fix_task', 'offset'))


def my_heatmap(x, y, s, bins=[np.arange(0, 1, 0.001),
                              np.arange(0, 1, 0.002)]):
    heatmap, x_edges, y_edges = np.histogram2d(x, y, bins=bins)
    heatmap = gaussian_filter(heatmap, sigma=s)
    extent = [x_edges[0], x_edges[-1], y_edges[-1], y_edges[0]]
    return heatmap.T, extent