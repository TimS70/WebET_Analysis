import os

import matplotlib.pyplot as plt
import seaborn as sns

from utils.path import makedir


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


def violin_plot(data_trial_fix, outcome, factor):

    fig, axes = plt.subplots(1, 1, sharey=True, figsize=(15, 6))
    fig.suptitle('Offset and precision')

    sns.violinplot(ax=axes,
                   x=factor,
                   y=outcome,
                   data=data_trial_fix)

    save_plot((factor + '_vs_' + outcome),
              'results', 'plots', 'fix_task', 'main_effect')
    plt.close()


def split_violin_plot(data_trial, outcome, factor, split_factor):
    fig, axes = plt.subplots(1, 1, sharey=False, figsize=(6, 6))
    fig.suptitle(outcome)

    ax = sns.violinplot(ax=axes,
                        x=factor,
                        y=outcome,
                        hue=split_factor,
                        split=True,
                        data=data_trial)
    save_plot(('split_violin_' + factor + '_vs_' + outcome + '_vs_' +
               split_factor),
              'results', 'plots', 'fix_task', 'main_effect')
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

    plt.show()

    makedir(*args)
    plt.savefig(os.path.join(*args, file_name), bbox_inches='tight')


def save_plot(file_name, *args):
    makedir(*args)
    path = os.path.join(*args)
    plt.savefig(os.path.join(path, file_name))
    print(
        f"""Plot {file_name} was saved to {path} \n"""
    )
