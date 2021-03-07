import matplotlib as plt
import numpy as np
import pandas as pd


def spaghetti_plot(data, xVar, yVar, highlighted_subject):
    plt.style.use('seaborn-darkgrid')
    fig, ax = plt.subplots(figsize=(15, 10))

    # Draw Plots
    for subject in data["run_id"].unique():
        ax.plot(data.loc[data['run_id']==subject, xVar],
                data.loc[data['run_id']==subject, yVar],
                marker='', color='grey', linewidth=1, alpha=0.4)

    # Highlight Subject
    ax.plot(data.loc[data['run_id'] == highlighted_subject, xVar],
            data.loc[data['run_id'] == highlighted_subject, yVar],
            marker='', color='orange', linewidth=4, alpha=0.7)

    # Let's annotate the plot
    for subject in data["run_id"].unique():
        if subject != highlighted_subject:
            ax.text(data.loc[data['run_id']==subject, xVar].max()+1,
                    data.loc[data['run_id']==subject, yVar].tail(1),
                    s=subject, horizontalalignment='left', size='small', color='grey')

        else:
            ax.text(data.loc[data['run_id']==subject, xVar].max()+1,
                    data.loc[data['run_id']==subject, yVar].tail(1),
                    s=subject, horizontalalignment='left', size='small', color='orange')
    return plt