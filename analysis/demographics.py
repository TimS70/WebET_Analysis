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

    data_subject = add_demographic_grouped_variable(
        data_subject, 'Current Country of Residence', 'residence',
        ['Poland', 'United Kingdom', 'United States'])

    data_subject = add_demographic_grouped_variable(
        data_subject, 'Nationality', 'nationality_grouped',
        ['Poland', 'United Kingdom', 'United States', 'Italy'])

    predictors = [
        'residence', 'nationality_grouped',
        'employment_status', 'Student Status', 'degree',
        'kind_of_correction', 'sight', 'vertPosition', 'webcam_fps',
        'ethnic', 'gender']

    demo_table = pd.DataFrame(columns=['variable', 'n', 'percent'])
    for predictor in predictors:
        freq_table = frequency_table(data_subject, predictor, save_table=True)

        sub_header = pd.DataFrame(
            [[freq_table.columns[0], ' ', ' ']],
            columns=list(freq_table.columns))

        freq_table = sub_header.append(freq_table)
        freq_table.columns = ['variable', 'n', 'percent']
        demo_table = demo_table.append(freq_table, ignore_index=True)

    print(demo_table)
    write_csv(demo_table, 'demographics.csv',
              'results', 'tables', 'demographics')

    # Only US sample
    demo_table = pd.DataFrame(columns=['variable', 'n', 'percent'])
    for predictor in predictors:
        freq_table = frequency_table(
            data_subject.loc[data_subject['residence']=='United States', :],
            predictor, save_table=False)

        sub_header = pd.DataFrame(
            [[freq_table.columns[0], ' ', ' ']],
            columns=list(freq_table.columns))

        freq_table = sub_header.append(freq_table)
        freq_table.columns = ['variable', 'n', 'percent']
        demo_table = demo_table.append(freq_table, ignore_index=True)

    print(demo_table)
    write_csv(demo_table, 'demographics_us.csv',
              'results', 'tables', 'demographics')




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


def add_demographic_grouped_variable(data_subject, old_column, new_column, categories):
    data_subject[new_column] = 'other'
    for col in categories:
        data_subject.loc[data_subject[old_column] == col, new_column] = col

    print(f"""Columns {new_column} was aggregated from {old_column}: \n"""
          f"""{frequency_table(data_subject, new_column)} \n""")

    return data_subject


def frequency_table(data_subject, predictor, save_table=True):
    freq_table = pd.crosstab(
            index=data_subject[predictor],
            columns="count") \
        .reset_index() \
        .assign(percent=lambda data_frame: data_frame['count'] /
                                           sum(data_frame['count'])) \
        .sort_values(by='count')

    # print(f"""{freq_table} \n""")

    if save_table:
        write_csv(freq_table, (predictor + '.csv'),
                  'results', 'tables', 'demographics')

    return freq_table


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
