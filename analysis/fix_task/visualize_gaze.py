import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.ndimage.filters import gaussian_filter

from utils.plots import save_plot


def fix_heatmap(data_et_fix):
    x = data_et_fix.loc[
        (data_et_fix['x'] > 0) & (data_et_fix['x'] < 1) &
        (data_et_fix['y'] > 0) & (data_et_fix['y'] < 1),
        'x']

    y = data_et_fix.loc[
        (data_et_fix['x'] > 0) & (data_et_fix['x'] < 1) &
        (data_et_fix['y'] > 0) & (data_et_fix['y'] < 1),
        'y']

    s = 34
    img, extent = myplot(x, y, s=s)

    plt.figure(figsize=(7, 7))
    plt.imshow(img, extent=extent, origin='upper', cmap=cm.Greens, aspect=(9 / 16))
    plt.title("Distribution of fixations after 1 second, $\sigma$ = %d" % s)

    xPos = [0.2, 0.5, 0.8, 0.2, 0.5, 0.8, 0.2, 0.5, 0.8]
    yPos = [0.2, 0.2, 0.2, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8]
    for i in range(0, len(xPos)):
        plt.text(xPos[i], yPos[i], '+', size=12, ha="center")

    save_plot('fix_heatmap.png', 'results', 'plots', 'fix_task')
    plt.close()


def myplot(x, y, s, bins=[1200, 675]):
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=bins)
    heatmap = gaussian_filter(heatmap, sigma=s)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    return heatmap.T, extent


def visualize_exemplary_run(data_plot):
    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(18, 12))
    axes = axes.ravel()
    xPos = [0.2, 0.5, 0.8, 0.2, 0.5, 0.8, 0.2, 0.5, 0.8]
    yPos = [0.2, 0.2, 0.2, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8]
    for i in range(0, 9):
        axes_data = data_plot.loc[
                    (data_plot['x_pos'] == xPos[i]) &
                    (data_plot['y_pos'] == yPos[i]), :]
        im = axes[i].scatter(
            axes_data['x'],
            axes_data['y'],
            c=axes_data['t_task'],
            cmap='viridis'
        )
        axes[i].set_ylim(0, 1)
        axes[i].set_xlim(0, 1)

    fig.colorbar(im, ax=axes)

    run = data_plot['run_id'].unique()[0]
    save_plot(('exemplary_run_' + str(run) + '.png'),
              'results', 'plots', 'fix_task')
    plt.close()
