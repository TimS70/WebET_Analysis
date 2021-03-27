import matplotlib.pyplot as plt

from visualize.all_tasks import save_plot


def plot_histogram(variable, file_name, path):
    plt.hist(variable, bins=50)
    plt.rc('font', size=10)
    save_plot(file_name, path)
    plt.close()


def plot_2d_histogram(x, y, file_name, path):
    plt.hist2d(x, y, bins=100)
    plt.rc('font', size=10)
    save_plot(file_name, path)
    plt.close()
