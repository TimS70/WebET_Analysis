import math
import os

import matplotlib.pyplot as plt
import pandas as pd

from visualize.all_tasks import save_plot
from utils.save_data import write_csv


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

    print(
        f"""Describe window size\n"""
        f"""{data_subject[['window_x', 'window_y']].describe()}"""
    )

    predictors = [
        'residence', 'nationality_grouped',
        'employment_status', 'Student Status', 'degree',
        'kind_of_correction', 'sight', 'vertPosition', 'webcam_fps',
        'ethnic', 'gender', 'browser']

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
    write_csv(data=demo_table, file_name='demographics.csv',
              path=os.path.join('results', 'tables', 'demographics'))

    # Only US sample
    demo_table = pd.DataFrame(columns=['variable', 'n', 'percent'])
    for predictor in predictors:
        freq_table = frequency_table(
            data_subject[data_subject['residence'] == 'United States'],
            predictor, save_table=False)

        sub_header = pd.DataFrame(
            [[freq_table.columns[0], ' ', ' ']],
            columns=list(freq_table.columns))

        freq_table = sub_header.append(freq_table)
        freq_table.columns = ['variable', 'n', 'percent']
        demo_table = demo_table.append(freq_table, ignore_index=True)

    print(demo_table)
    write_csv(data=demo_table, file_name='demographics_us.csv',
              path=os.path.join('results', 'tables', 'demographics'))

    plot_pie_charts(data_subject, predictors)

    n_bins = 10
    plt.hist(data_subject['age'], bins=n_bins)
    plt.title('Age histogram (bins=' + str(n_bins) + ')')
    plt.xlabel('Age')
    plt.ylabel('Frequency')

    print(f"""Describe age: \n"""
          f"""{data_subject['age'].describe()}""")

    save_plot(file_name='age.png',
              path=os.path.join('results', 'plots', 'demographics'))
    plt.close()

    compare_us_vs_int_sample(
        data_subject=data_subject,
        path_table=os.path.join('results', 'tables', 'demographics')
    )


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
        .assign(percent=lambda data_frame: round(100 * data_frame['count'] /
                                           sum(data_frame['count']), 2)) \
        .sort_values(by='count', ascending=False)

    # print(f"""{freq_table} \n""")

    if save_table:
        write_csv(data=freq_table, file_name=predictor + '.csv',
                  path=os.path.join('results', 'tables', 'demographics'))

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

    save_plot(file_name='pie_charts.png',
              path=os.path.join('results', 'plots',
                                'demographics'))
    plt.close()


def cross_tab(col, data_subject):
    pie = pd.crosstab(
        index=data_subject[col],
        columns="count") \
        .reset_index() \
        .sort_values(by='count')
    pie.columns = [col, 'count']
    return pie


def compare_us_vs_int_sample(path_table, data_subject=None, path_data_subject=None):

    if data_subject is None:
        data_subject = pd.read_csv(os.path.join(path_data_subject))

    data_subject['residence'] = data_subject['Current Country of Residence']

    runs_not_us = data_subject.loc[
        data_subject['residence'] != 'United States', 'run_id']

    data_subject['residence'] = 'us'
    data_subject.loc[
        data_subject['run_id'].isin(runs_not_us),
        'residence'] = 'international'

    grouped_us = data_subject.groupby(
        ['residence'],
        as_index=False).agg(
        n=('run_id', 'count'),
        attributeIndex=('attributeIndex', 'mean'),
        attributeIndex_std=('attributeIndex', 'std'),
        optionIndex=('optionIndex', 'mean'),
        optionIndex_std=('optionIndex', 'std'),
        payneIndex=('payneIndex', 'mean'),
        payneIndex_std=('payneIndex', 'std'),
        choseLL=('choseLL', 'mean'),
        choseLL_std=('choseLL', 'std'),
        choseTop=('choseTop', 'mean'),
        choseTop_std=('choseTop', 'std'),
        logK=('logK', 'mean'),
        logK_std=('logK', 'std'),
        choice_rt=('choice_rt', 'mean'),
        choice_rt_std=('choice_rt', 'std'),
        offset=('offset', 'mean'),
        offset_std=('offset', 'std'),
        precision=('precision', 'mean'),
        precision_std=('precision', 'std'),
        fps=('fps', 'mean'),
        fps_std=('fps', 'std')).T

    write_csv(
        data=grouped_us,
        file_name='us_vs_international_sample.csv',
        path=path_table
    )

    print(
        f"""grouped_us.transpose: \n"""
        f"""{grouped_us} \n"""
    )