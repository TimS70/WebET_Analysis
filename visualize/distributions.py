import numpy as np

import matplotlib.pyplot as plt

from visualize.all_tasks import save_plot


def plot_histogram(variable, file_name, path, n_bins=50):
    plt.hist(variable, bins=n_bins)
    plt.xlim(0, 1)
    plt.ylim(1, 0)
    save_plot(file_name, path)
    plt.close()


def plot_2d_histogram(x, y, file_name, path):
    plt.scatter(x, y, s=0.5, label='xy participant mean')

    plt.xlim(0, 1)
    plt.ylim(1, 0)
    plt.xticks(np.arange(0, 1, 0.1))
    plt.yticks(np.arange(0, 1, 0.1))

    plt.legend()
    plt.xlabel('X [%]')
    plt.ylabel('Y [%]')
    plt.grid()
    plt.tight_layout()
    plt.box(False)
    plt.title('x_participant_mean, y_participant_mean')

    save_plot(file_name, path)
    plt.close()
