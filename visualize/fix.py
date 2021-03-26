import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


from visualize.all_tasks import save_plot, my_heatmap


def hist_plots_quality(data_subject):

    font_size = 15
    plt.rcParams.update({'font.size': font_size})

    plt.hist(data_subject['precision'], bins=20)
    plt.title('Precision histogram')
    save_plot('precision_participants.png', 'results', 'plots', 'fix_task')
    plt.close()

    plt.hist(data_subject['offset'], bins=20)
    plt.title('Offset histogram')
    save_plot('offset_participants.png', 'results', 'plots', 'fix_task')
    plt.close()

    plt.hist(data_subject['fps'], bins=20)
    plt.title('FPS histogram')
    save_plot('fps_participants_cleaned.png', 'results', 'plots', 'fix_task')
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

        ax.imshow(img, extent=extent, origin='upper', cmap=cm.Greens, aspect=(9 / 16))
        ax.set_xlim(0, 1)
        ax.set_ylim(1, 0)
        ax.set_title("Distribution of fixations after 1 second, $\sigma$ = %d" % s)

        x_pos = [0.2, 0.5, 0.8, 0.2, 0.5, 0.8, 0.2, 0.5, 0.8]
        y_pos = [0.2, 0.2, 0.2, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8]
        for i in range(0, len(x_pos)):
            plt.text(x_pos[i], y_pos[i], '+', size=12, ha="center")

        save_plot(str(run) + '.png', 'results', 'plots', 'fix_task', 'heatmaps')
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
    save_plot(('exemplary_run_' + str(run) + '.png'),
              'results', 'plots', 'fix_task')
    plt.close()
