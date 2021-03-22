import math
import os

import matplotlib.pyplot as plt
import pandas as pd

from visualize.all_tasks import save_plot
from utils.tables import write_csv


def analyze_demographics():

    print('################################### \n'
          'Analyze demographics \n'
          '################################### \n')

    data_subject = pd.read_csv(
        os.path.join('data', 'all_trials', 'cleaned', 'data_subject.csv'))
    data_subject['kind_of_correction'] = data_subject['glasses']

    predictors = [
        'Current Country of Residence', 'Nationality',
        'employment_status', 'Student Status', 'degree',
        'kind_of_correction', 'sight', 'vertPosition', 'webcam_fps',
        'ethnic', 'gender']

    frequency_tables(data_subject, predictors)
    plot_pie_charts(data_subject, predictors)

    n_bins = 10
    plt.hist(data_subject['birthyear'], bins=n_bins)
    plt.title('Birthyear histogram (bins=' + str(n_bins) + ')')
    plt.xlabel('Birthyear')
    plt.ylabel('Frequency')


    age = 2021 - data_subject['birthyear']
    print(
        f"""Describe age: \n"""
        f"""{age.describe()}""")

    save_plot('birthyear.png',
              'results', 'plots', 'demographics')
    plt.close()


def frequency_tables(data_subject, predictors):

    for col in predictors:

        freq_table = pd.crosstab(
                index=data_subject[col],
                columns="count")
        freq_table.reset_index()
        freq_table['percent'] = freq_table['count'] / sum(freq_table['count'])

        print(f"""{freq_table} \n""")

        write_csv(freq_table, (col + '.csv'),
                  'results', 'tables', 'demographics')


def plot_pie_charts(data_subject, predictors):

    n_cols = 4
    n_row = math.ceil(len(predictors)/n_cols)

    fig, ax = plt.subplots(nrows=n_row, ncols=n_cols,
                           figsize=((5*n_cols), (5*n_row)))
    fig.suptitle('Pie charts', fontsize=20)
    ax = ax.ravel()

    for i in range(0, len(predictors)):
        pie = cross_tab(predictors[i], data_subject)
        ax[i].pie(pie['count'], labels=pie[predictors[i]], autopct='%1.1f%%', startangle=90)
        ax[i].axis('equal')
        ax[i].set_title(predictors[i], pad=20)

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
