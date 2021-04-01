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


def spaghetti_plot(data, x_var, y_var, highlighted_subject):
    plt.style.use('seaborn-darkgrid')
    fig, ax = plt.subplots(figsize=(15, 10))

    # Draw Plots
    for subject in data["run_id"].unique():
        ax.plot(data.loc[data['run_id'] == subject, x_var],
                data.loc[data['run_id'] == subject, y_var],
                marker='', color='grey', linewidth=1, alpha=0.4)

    # Highlight Subject
    ax.plot(data.loc[data['run_id'] == highlighted_subject, x_var],
            data.loc[data['run_id'] == highlighted_subject, y_var],
            marker='', color='orange', linewidth=4, alpha=0.7)

    # Let's annotate the plot
    for subject in data["run_id"].unique():
        if subject != highlighted_subject:
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
    fig, ax = plt.subplots(nrows=2, ncols=4, figsize=(16, 10))
    fig.suptitle(outcome + ' for various categorical predictors', fontsize=20)
    plt.subplots_adjust(hspace=0.5)

    ax = ax.ravel()

    for i in range(0, 8):
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


def scatter_matrix(data, corr_variables, file_name, path_target, factor=None):
    sns.set()

    if factor is None:
        sns.pairplot(data[corr_variables],
                     kind='reg',
                     corner=True)
    else:
        sns.pairplot(
            data[np.append(corr_variables, [factor])],
            hue=factor,
            kind='reg',
            corner=True)

    save_plot(file_name=file_name,
              path=path_target,
              message=True)
    plt.close()


def corr_matrix(data_plot, corr_columns, option,
                file_name, *args):

    this_corr_matrix = np.corrcoef(
        data_plot.loc[:, corr_columns].T)

    if option == 'table_p':
        corr_table_p = data_plot[corr_columns].rcorr()
        write_csv(
            corr_table_p,
            file_name,
            *args)

    if option == 'table_n':
        corr_table_n = data_plot[corr_columns].rcorr(upper='n')
        write_csv(
            corr_table_n,
            file_name,
            *args)

    if option == 'heatmap':
        smg.plot_corr(this_corr_matrix, xnames=corr_columns)
        makedir('results', 'plots', 'choice_task')
        save_plot(file_name=file_name,
                  path=os.path.join(*args))
        plt.close()


def save_table_as_plot(data_frame, file_name, *args):
    fig, ax = plt.subplots()
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')

    ax.table(
        cellText=data_frame.values,
        colLabels=data_frame.columns,
        loc='center')

    fig.tight_layout()

    save_plot(file_name=file_name, path=os.path.join(*args))
    plt.close()


def save_plot(file_name, path, message=False):
    makedir(path)
    plt.savefig(os.path.join(path, file_name))

    if message:
        print(f"""Plot {file_name} was saved to {path} """)


