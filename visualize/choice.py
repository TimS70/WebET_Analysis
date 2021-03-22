import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns

from utils.data_frames import merge_by_index
from visualize.all_tasks import save_plot, my_heatmap


def plot_aoi_scatter(data_et):
    data_plot = data_et.loc[data_et['aoi'] != 0, ['x', 'y']]
    x = data_plot['x']
    y = data_plot['y']
    plt.scatter(x, y, s=0.1)
    plt.ylim(1, 0)
    plt.xlim(0, 1)
    save_plot('aoi_scatter.png', 'results', 'plots', 'choice_task', 'et')
    plt.close()


def plot_choice_task_heatmap(data_et):
    x = data_et.loc[data_et['t_task'] > 1000, 'x']
    y = data_et.loc[data_et['t_task'] > 1000, 'y']

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(7, 7))

    s = 34
    img, extent = my_heatmap(x, y, s=s)
    ax.imshow(img, extent=extent, origin='upper', cmap=cm.Greens, aspect=(9 / 16))
    ax.set_xlim(0, 1)
    ax.set_ylim(1, 0)
    # rect = patches.Rectangle((0.05, 0.05), 0.9, 0.4, linewidth=1, edgecolor='black', facecolor='none')
    # ax.add_patch(rect)
    # rect = patches.Rectangle((0.05, 0.55), 0.9, 0.4, linewidth=1, edgecolor='black', facecolor='none')
    # ax.add_patch(rect)
    #
    # x_pos = [0.25, 0.75, 0.25, 0.75]
    # y_pos = [0.25, 0.25, 0.75, 0.75]
    # for i in range(0, len(x_pos)):
    #     plt.text(x_pos[i], y_pos[i], '[attribute]', size=15, ha="center")

    ax.set_title("Distribution of fixations after 1 second, $\sigma$ = %d" % s)

    save_plot(
        'choice_heatmap.png',
        'results', 'plots', 'choice_task', 'et')
    plt.close()


def plot_example_eye_movement(data_et, data_trial, run):
    data_plot = data_et.loc[data_et['run_id'] == run, :]

    data_plot = merge_by_index(
        data_plot, data_trial, 'trial_duration_exact')

    data_plot['t_task_rel'] = \
        data_plot['t_task'] / data_plot['trial_duration_exact']

    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(17, 10))
    axes = axes.ravel()

    this_subject = data_plot['run_id'].unique()[0]
    for i in range(0, 9):
        df_this_trials = data_trial.loc[
                         (data_trial['run_id'] == this_subject) &
                         (data_trial['withinTaskIndex'] == 50 + i + 1), :]

        payne = df_this_trials['payneIndex'].values

        axes_data = data_plot.loc[data_plot['withinTaskIndex'] == i + 1, :]
        image = axes[i].scatter(axes_data['x'], axes_data['y'], c=axes_data['t_task_rel'], cmap='viridis')
        axes[i].set_title('Trial Nr: ' + str(i + 1) + ' / ' + str(payne))
        axes[i].set_ylim(1, 0)
        axes[i].set_xlim(0, 1)

        # JS and python y coordinates seem to be inverted
        axes[i].text(0.25, 0.75, df_this_trials['option_TL'].values,
                     size=12, ha="center", transform=axes[i].transAxes)
        axes[i].text(0.25, 0.25, df_this_trials['option_BL'].values,
                     size=12, ha="center", transform=axes[i].transAxes)
        axes[i].text(0.75, 0.75, df_this_trials['option_TR'].values,
                     size=12, ha="center", transform=axes[i].transAxes)
        axes[i].text(0.75, 0.25, df_this_trials['option_BR'].values,
                     size=12, ha="center", transform=axes[i].transAxes)

    fig.colorbar(image, ax=axes)

    save_plot(('example_' + str(round(run, 0)) + '.png'),
              'results', 'plots', 'choice_task', 'et')
    plt.close()
    
    
def plot_categorical_confounders(data_subject):
    predictors = ['chinFirst', 'ethnic', 'degree', 'Student Status']
    outcome = 'choseLL'

    fig, ax = plt.subplots(nrows=1, ncols=4, figsize=(16, 5))
    fig.suptitle(outcome + ' for various categorical predictors', fontsize=20)
    plt.subplots_adjust(hspace=0.5)

    ax = ax.ravel()

    for i in range(0, 4):
        sns.boxplot(ax=ax[i], x=predictors[i], y=outcome,
                    data=data_subject)

        ax[i].tick_params(labelrotation=45, labelsize=13)
        ax[i].tick_params(axis='y', labelrotation=None)

        nobs = data_subject[predictors[i]].value_counts().values
        nobs = [str(x) for x in nobs.tolist()]
        nobs = ["n: " + i for i in nobs]
        # Add it to the plot
        pos = range(len(nobs))

        max_value = data_subject[outcome].max()
        y_pos = max_value + max_value * 0.15

        for tick, label in zip(pos, ax[i].get_xticklabels()):
            ax[i].text(
                pos[tick], y_pos, nobs[tick],
                verticalalignment='top',
                horizontalalignment='center', size=13, weight='normal')

    plt.tight_layout()
    save_plot('cat_variables.png', 'results', 'plots', 'choice_task')
