import numpy as np

import matplotlib.pyplot as plt

from visualize.all_tasks import save_plot


def plot_histogram(variable, file_name, path):
    plt.hist(variable, bins=50)
    plt.xlim(0, 1)
    plt.ylim(1, 0)
    save_plot(file_name, path)
    plt.close()


def plot_2d_histogram(x, y, file_name, path):
    plt.imshow(np.histogram2d(x, y, bins=200))
    plt.xlim(0, 1)
    plt.ylim(1, 0)
    save_plot(file_name, path)
    plt.close()
