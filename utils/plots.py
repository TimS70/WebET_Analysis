import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


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
