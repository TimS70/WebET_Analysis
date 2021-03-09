import os

import matplotlib.pyplot as plt
import pandas as pd

from utils.path import makedir


def show_demographics(data_subject):
    makedir('plots', 'demographics')
    frequency_tables(data_subject)
    plot_pie_charts(data_subject)
    plt.hist(data_subject['birthyear'], bins=15)
    plt.savefig(os.path.join('plots', 'demographics', 'age.png'))


def frequency_tables(data_subject):
    columns = ['Current Country of Residence', 'Nationality',
               'employment_status', 'webcam_fps', 'ethnic',
               'gender']

    for col in columns:
        print(pd.crosstab(index=data_subject[col],
                          columns="count")
              )
        print('\n')


def plot_pie_charts(data_subject):
    fig, ax = plt.subplots(nrows=4, ncols=2, figsize=(10, 20))
    fig.suptitle('Pie charts', fontsize=20)
    ax = ax.ravel()

    predictors = [
        'ethnic', 'employment_status', 'vertPosition', 'degree',
        'glasses', 'sight', 'Student Status'
    ]
    for i in range(0, len(predictors)):
        pie = cross_tab(predictors[i], data_subject)
        ax[i].pie(pie['count'], labels=pie[predictors[i]], autopct='%1.1f%%', startangle=90)
        ax[i].axis('equal')
        ax[i].set_title(predictors[i])
    plt.savefig(os.path.join('plots', 'demographics', 'pie_charts.png'))


def cross_tab(col, data_subject):
    pie = pd.crosstab(
        index=data_subject[col],
        columns="count") \
        .reset_index() \
        .sort_values(by='count')
    pie.columns = [col, 'count']
    return pie
