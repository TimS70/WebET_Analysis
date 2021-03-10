import os

import matplotlib.pyplot as plt
import pandas as pd

from utils.path import makedir
from utils.plots import save_plot
from utils.tables import write_csv


def show_demographics():

    print('################################### \n'
          'Analyze demographics \n'
          '################################### \n')

    data_subject = pd.read_csv(
        os.path.join('data', 'all_trials', 'cleaned', 'data_subject.csv'))

    frequency_tables(data_subject)
    plot_pie_charts(data_subject)
    plt.hist(data_subject['birthyear'], bins=15)

    save_plot('age.png',
              'results', 'plots', 'demographics')
    plt.close()


def frequency_tables(data_subject):
    columns = ['Current Country of Residence', 'Nationality',
               'employment_status', 'webcam_fps', 'ethnic',
               'gender']

    for col in columns:

        freq_table = pd.crosstab(
            index=data_subject[col],
            columns="count")

        print(f"""{freq_table} \n""")

        write_csv(freq_table, (col + '.csv'),
                  'results', 'tables', 'demographics')


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

    save_plot('pie_charts.png',
              'results', 'plots', 'demographics')
    plt.close()

def cross_tab(col, data_subject):
    pie = pd.crosstab(
        index=data_subject[col],
        columns="count") \
        .reset_index() \
        .sort_values(by='count')
    pie.columns = [col, 'count']
    return pie
