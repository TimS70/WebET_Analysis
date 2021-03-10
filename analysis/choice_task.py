import os

import matplotlib.cm as cm
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.ndimage.filters import gaussian_filter

from data_prep.cleaning.corr_data import clean_corr_data
from utils.data_frames import merge_by_index
from utils.path import makedir
from utils.plots import corr_matrix, corr_plot_split
from utils.tables import summarize_datasets


def analyze_choice_task(use_adjusted_et_data=True):

    print('################################### \n'
          'Analyze choice data \n'
          '################################### \n')

    data_et_uncorrected = pd.read_csv(
        os.path.join('data', 'choice_task', 'uncorrected', 'data_et.csv'))

    data_et_adjusted = pd.read_csv(
        os.path.join('data', 'choice_task', 'adjusted', 'data_et.csv'))

    if use_adjusted_et_data:

        data_trial = pd.read_csv(
            os.path.join(
                'data', 'choice_task', 'adjusted', 'data_trial.csv'))
        data_subject = pd.read_csv(
            os.path.join(
                'data', 'choice_task', 'adjusted', 'data_subject.csv'))

    else:
        data_trial = pd.read_csv(
            os.path.join(
                'data', 'choice_task', 'uncorrected', 'data_trial.csv'))
        data_subject = pd.read_csv(
            os.path.join(
                'data', 'choice_task', 'uncorrected', 'data_subject.csv'))

    print('Imported from data/choice_task/ with data_et_adjusted: ')
    summarize_datasets(data_et_adjusted, data_trial, data_subject)
    print('Imported from data/choice_task/ with data_et_uncorrected: ')
    summarize_datasets(data_et_uncorrected, data_trial, data_subject)

    plot_categorical_confounders(data_subject)
    plot_example_eye_movement(
        data_et_uncorrected, data_trial, data_subject, run=128)
    plot_choice_task_heatmap(data_et_uncorrected)
    corr_analysis_subject(data_subject)
    corr_analysis_trial(data_trial)


def plot_categorical_confounders(data_subject):
    predictors = ['chinFirst', 'ethnic', 'degree', 'Student Status']
    outcome = 'choseLL'

    fig, ax = plt.subplots(nrows=1, ncols=4, figsize=(16, 5))
    fig.suptitle(outcome + ' for various categorical predictors', fontsize=20)
    plt.subplots_adjust(hspace=0.5)

    ax = ax.ravel()

    for i in range(0, 4):
        sns.boxplot(ax=ax[i], x=predictors[i], y=outcome, data=data_subject)

        ax[i].tick_params(labelrotation=45, labelsize=13)
        ax[i].tick_params(axis='y', labelrotation=None)

        nobs = data_subject[predictors[i]].value_counts().values
        nobs = [str(x) for x in nobs.tolist()]
        nobs = ["n: " + i for i in nobs]
        # Add it to the plot
        pos = range(len(nobs))

        max_value = data_subject[outcome].max()
        y_pos = max_value + max_value * 0.1

        for tick, label in zip(pos, ax[i].get_xticklabels()):
            ax[i].text(
                pos[tick], y_pos, nobs[tick],
                verticalalignment='top',
                horizontalalignment='center', size=13, weight='normal')

    makedir('results', 'plots', 'choice_task')
    plt.savefig(
        os.path.join('results', 'plots', 'choice_task',
                     'cat_variables.png'))


# noinspection PyUnboundLocalVariable
def plot_example_eye_movement(data_et, data_trial, data_subject, run):
    data_plot = data_et.loc[data_et['run_id'] == run, :]

    data_plot = merge_by_index(
        data_plot, data_trial, 'trial_duration_exact')

    data_plot['t_task_rel'] = \
        data_plot['t_task'] / data_plot['trial_duration_exact']

    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(17, 10))
    axes = axes.ravel()

    this_subject = data_plot['run_id'].unique()[0]
    print(data_subject.loc[data_subject['run_id'] == this_subject, 'fps'])
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

    makedir('results', 'plots', 'choice_task')
    plt.savefig(
        os.path.join(
            'results', 'plots', 'choice_task',
            ('example_' + str(run) + '.png')))


# noinspection PyUnresolvedReferences
def plot_choice_task_heatmap(data_et):
    x = data_et.loc[data_et['t_task'] > 1000, 'x']
    y = data_et.loc[data_et['t_task'] > 1000, 'y']

    # noinspection PyUnresolvedReferences,PyShadowingNames
    def my_plot(x, y, s, bins=[1200, 675]):
        heatmap, x_edges, y_edges = np.histogram2d(x, y, bins=bins)
        heatmap = gaussian_filter(heatmap, sigma=s)
        extent = [x_edges[0], x_edges[-1], y_edges[-1], y_edges[0]]
        return heatmap.T, extent

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(7, 7))

    s = 34
    img, extent = my_plot(x, y, s=s)
    ax.imshow(img, extent=extent, origin='upper', cmap=cm.Greens, aspect=(9 / 16))

    rect = patches.Rectangle((0.05, 0.05), 0.9, 0.4, linewidth=1, edgecolor='black', facecolor='none')
    ax.add_patch(rect)
    rect = patches.Rectangle((0.05, 0.55), 0.9, 0.4, linewidth=1, edgecolor='black', facecolor='none')
    ax.add_patch(rect)

    x_pos = [0.25, 0.75, 0.25, 0.75]
    y_pos = [0.25, 0.25, 0.75, 0.75]
    for i in range(0, len(x_pos)):
        plt.text(x_pos[i], y_pos[i], '[attribute]', size=12, ha="center")

    ax.set_title("Distribution of fixations after 1 second, $\sigma$ = %d" % s)

    # plt.show()

    makedir('results', 'plots', 'choice_task')
    plt.savefig(
        os.path.join(
            'results', 'plots', 'choice_task', 'choice_heatmap.png'))


def corr_analysis_subject(data_subject):
    data_plot = clean_corr_data(
        data_subject.loc[:, [
                                'run_id', 'chinFirst', 'age', 'choseLL',
                                'attributeIndex', 'optionIndex', 'payneIndex',
                                'choice_rt']])

    corr_columns = [
        'age', 'choseLL',
        'attributeIndex', 'optionIndex', 'payneIndex',
        'choice_rt'
    ]

    corr_plot_split(data_plot, corr_columns,
                    'corr_vars_vs_chinFirst_trial.png', 'chinFirst',
                    'results', 'plots', 'choice_task')

    corr_matrix(data_plot, corr_columns,
                'table_p', 'subject_corr_p.csv',
                'results', 'tables', 'choice_task')
    corr_matrix(data_plot, corr_columns,
                'table_n', 'subject_corr_n.csv',
                'results', 'tables', 'choice_task')
    corr_matrix(data_plot, corr_columns,
                'heatmap', 'subject_corr_heatmap.png',
                'results', 'plots', 'choice_task')


def corr_analysis_trial(data_trial):
    data_plot = clean_corr_data(
        data_trial.loc[:, [
                              'run_id', 'chinFirst', 'choseLL', 'k',
                              'attributeIndex', 'optionIndex', 'payneIndex',
                              'trial_duration_exact']])

    corr_columns = [
        'choseLL', 'k', 'attributeIndex',
        'optionIndex', 'payneIndex', 'trial_duration_exact']

    corr_plot_split(data_plot, corr_columns,
                    'corr_vars_vs_chinFirst_trial.png', 'chinFirst',
                    'results', 'plots', 'choice_task')

    corr_columns = [
        'chinFirst', 'choseLL', 'k', 'attributeIndex',
        'optionIndex', 'payneIndex', 'trial_duration_exact']

    corr_matrix(data_plot, corr_columns,
                'table_p', 'trial_corr_p.csv',
                'results', 'tables', 'choice_task')
    corr_matrix(data_plot, corr_columns,
                'table_n', 'trial_corr_n.csv',
                'results', 'tables', 'choice_task')
    corr_matrix(data_plot, corr_columns,
                'heatmap', 'trial_corr_heatmap.png',
                'results', 'plots', 'choice_task')
