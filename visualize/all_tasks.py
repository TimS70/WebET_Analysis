import os

import matplotlib.pyplot as plt
import numpy as np
# noinspection PyUnresolvedReferences
import pingouin as pg
import seaborn as sns
import statsmodels.graphics.api as smg

from scipy.ndimage.filters import gaussian_filter

from inference.F import anova_outcomes_factor
from utils.path import makedir
from utils.save_data import write_csv


def spaghetti_plot(data, x_var, y_var, highlighted_run):
    plt.style.use('seaborn-darkgrid')
    fig, ax = plt.subplots(figsize=(15, 10))

    # Draw Plots
    for subject in data["run_id"].unique():
        ax.plot(data.loc[data['run_id'] == subject, x_var],
                data.loc[data['run_id'] == subject, y_var],
                marker='', color='grey', linewidth=1, alpha=0.4)

    # Highlight Subject
    ax.plot(data.loc[data['run_id'] == highlighted_run, x_var],
            data.loc[data['run_id'] == highlighted_run, y_var],
            marker='', color='orange', linewidth=4, alpha=0.7)

    # Let's annotate the plot
    for subject in data["run_id"].unique():
        if subject != highlighted_run:
            ax.text(data.loc[data['run_id'] == subject, x_var].max() + 1,
                    data.loc[data['run_id'] == subject, y_var].tail(1),
                    s=subject, horizontalalignment='left', size='small', color='grey')

        else:
            ax.text(data.loc[data['run_id'] == subject, x_var].max() + 1,
                    data.loc[data['run_id'] == subject, y_var].tail(1),
                    s=subject, horizontalalignment='left', size='small', color='orange')
    return plt


def violin_plot(data, outcome, factor, path, split_factor=None):

    fig, axes = plt.subplots(1, 1, sharey='none', figsize=(6, 6))
    fig.suptitle('Offset and precision')

    if split_factor is None:
        sns.violinplot(ax=axes,
                       x=factor, y=outcome,
                       data=data)
    else:
        sns.violinplot(ax=axes,
                       x=factor, y=outcome, hue=split_factor,
                       split=True,
                       data=data)

    save_plot(file_name=factor + '_vs_' + outcome + '.png',
              path=path)
    plt.close()


def get_box_plots(data, outcome, predictors, file_name, path_target):

    if len(predictors) > 4:
        n_rows = 2
    else:
        n_rows = 1
    fig, ax = plt.subplots(nrows=n_rows, ncols=4, figsize=(n_rows * 6, 10))
    fig.suptitle(outcome + ' for various categorical predictors', fontsize=20)
    plt.subplots_adjust(hspace=0.5)

    ax = ax.ravel()

    for i in range(0, len(predictors)):
        sns.boxplot(ax=ax[i], x=predictors[i], y=outcome, data=data)

        ax[i].tick_params(labelrotation=45, labelsize=13)
        ax[i].tick_params(axis='y', labelrotation=None)

        nobs = data[predictors[i]].value_counts().values
        nobs = [str(x) for x in nobs.tolist()]
        nobs = ["n: " + i for i in nobs]
        # Add it to the plot
        pos = range(len(nobs))

        max_value = data[outcome].max()
        y_pos = max_value + max_value * 0.1

        for tick, label in zip(pos, ax[i].get_xticklabels()):
            ax[i].text(
                pos[tick], y_pos, nobs[tick],
                verticalalignment='top',
                horizontalalignment='center', size=13, weight='normal')

    save_plot(file_name=file_name,
              path=path_target,
              message=True)
    plt.close()


def save_plot(file_name, path, message=False):
    makedir(path)
    plt.savefig(os.path.join(path, file_name))

    if message:
        print(f"""Plot {file_name} was saved to {path} """)


