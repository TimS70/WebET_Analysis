import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data_prep.cleaning.prolific_ids import drop_duplicate_ids
from utils.add_next_trial import add_next_trial
from utils.data_frames import merge_by_subject
from visualize.all_tasks import save_plot
from utils.tables import write_csv
from visualize.dropouts import plot_incomplete_runs


def analyze_dropouts():

    print('################################### \n'
          'Analyze dropouts \n'
          '################################### \n')

    data_subject = pd.read_csv(
        os.path.join('data', 'all_trials', 'added_var',
                     'data_subject.csv'))
    data_trial = pd.read_csv(
        os.path.join('data', 'all_trials', 'added_var',
                     'data_trial.csv')) \

    data_trial = merge_by_subject(data_trial, data_subject,
                                  'prolificID', 'status')

    # Filter those from prolific
    data_subject = data_subject[
        pd.notna(data_subject['prolificID'])]
    data_trial = data_trial[
        data_trial['run_id'].isin(data_subject['run_id'])]

    dropouts_participants(data_subject, data_trial)

    # Check incomplete runs
    report_incomplete_runs(data_trial)
    dropout_by_task_nr(data_trial)
    dropout_by_type(data_trial)
    check_calibration(data_trial)
    multi_participation_by_type(data_trial)


def report_incomplete_runs(data_trial):
    max_trial_by_run = data_trial \
        .groupby(['run_id'], as_index=False).agg(
            trial_index=('trial_index', 'max')) \
        .merge(
            data_trial[['run_id', 'trial_index',
                        'chinFirst', 'prolificID',
                        'trial_type_new', 'status']],
            on=['run_id', 'trial_index'],
            how='left')

    max_trial_by_run = add_next_trial(max_trial_by_run, data_trial)


    data_incomplete_runs = max_trial_by_run[
        max_trial_by_run['trial_type_new'] != 'end']

    dropout_rate = len(data_incomplete_runs['run_id']) / \
                   len(max_trial_by_run['run_id'].unique())

    summary_data_trial = pd.DataFrame({
        'names': [
            'run_id',
            'prolificID'],
        'n': [
            len(max_trial_by_run['run_id'].unique()),
            len(max_trial_by_run['prolificID'].unique())
        ],
        'n_approved': [
            '-',
            len(max_trial_by_run.loc[
                    max_trial_by_run['status'] == 'APPROVED',
                    'prolificID'].unique())]
    })

    print(
        f"""{summary_data_trial} \n"""
        f"""n={len(data_incomplete_runs['run_id'])} """
        f"""incomplete runs """
        f"""({round(100 * dropout_rate, 2)}%) \n""")


def dropouts_participants(data_subject, data_trial):

    # Mark participants with trials
    data_subject['status_2_id'] = np.nan
    data_subject.loc[
        ~data_subject['run_id'].isin(data_trial['run_id']),
        'status_2_id'] = 'no_trials'

    runs_returned_no_trials = data_subject.loc[
              (data_subject['status'] == 'RETURNED') &
              (data_subject['status_2_id'] == 'no_trials'),
              'prolificID'].unique()
    print(f"""Returned and no trials: {len(runs_returned_no_trials)}""")

    # Check for multiple attempts
    print('Attempts in total')
    attempts_by_id = multi_participation_by_run(data_trial)

    print('Attempts approved')
    ids_one_attempt, ids_multiple_attempts = multi_participation_by_run(
        data_trial[data_trial['status'] == 'APPROVED'])

    data_subject.loc[
        data_subject['prolificID'].isin(ids_one_attempt),
        'status_2_id'] = 'one_attempt'

    data_subject.loc[
        data_subject['prolificID'].isin(ids_multiple_attempts),
        'status_2_id'] = 'multiple_attempts'

    print('Attempts not approved')
    ids_one_attempt, ids_multiple_attempts = multi_participation_by_run(
        data_trial[data_trial['status'] != 'APPROVED'])

    data_subject.loc[
        data_subject['prolificID'].isin(ids_one_attempt),
        'status_2_id'] = 'one_attempt'

    data_subject.loc[
        data_subject['prolificID'].isin(ids_multiple_attempts),
        'status_2_id'] = 'multiple_attempts'

    # Conclusions
    print(
        f"""Approved: {len(data_subject[
                               data_subject['status'] == 'APPROVED'])} \n"""
        f"""Not Approved: {len(data_subject[
                               data_subject['status'] != 'APPROVED'])} \n"""
    )

    freq_table_status = pd.crosstab(
              index=drop_duplicate_ids(data_subject)['status'],
              columns="n")
    print(f"""Freq_table status: {freq_table_status} \n""")

    freq_table_status = pd.crosstab(
              index=drop_duplicate_ids(data_subject[
                  data_subject['status_2_id'] == 'no_trials'])['status'],
              columns="n")
    print(f"""Freq_table status no_trials: {freq_table_status} \n""")

    freq_table_status = pd.crosstab(
              index=drop_duplicate_ids(data_subject[
                  data_subject['status_2_id'] != 'no_trials'])['status'],
              columns="n")
    print(f"""Freq_table status has trials: {freq_table_status} \n""")

    print(f"""Freq_table status_2_d: \n"""
          f"""{pd.crosstab(
              index=drop_duplicate_ids(data_subject)['status_2_id'], 
              columns="n")} \n""")

    print(f"""Freq_table status_2_d approved: \n"""
          f"""{pd.crosstab(
              index=drop_duplicate_ids(data_subject[
                  data_subject['status'] == 'APPROVED'])['status_2_id'], 
              columns="n")} \n""")

    print(f"""Freq_table status_2_d not approved: \n"""
          f"""{pd.crosstab(
              index=drop_duplicate_ids(data_subject[
                  data_subject['status'] != 'APPROVED'])['status_2_id'], 
              columns="n")} \n""")


def dropout_by_task_nr(data_trial):

    max_trial_by_run = data_trial \
        .groupby(['run_id'], as_index=False).agg(
            max_trial=('trial_index', 'max')) \
        .merge(
            data_trial[['run_id', 'trial_index', 'prolificID',
                        'trial_type_nr', 'task_nr_new',
                        'status']] \
                .rename(columns={'trial_index': 'max_trial'}),
            on=['run_id', 'max_trial'],
            how='left')

    max_trial_by_nr = max_trial_by_run \
        .groupby(['task_nr_new'], as_index=False) \
        .agg(n=('run_id', 'count')) \
        .sort_values(by='n')

    print(
        f"""Dropout by task nr: \n"""
        f"""{max_trial_by_nr} \n"""
    )

    write_csv(
        max_trial_by_nr,
        'dropout_by_task_nr.csv',
        'results', 'tables', 'dropouts')


def group_last_trial_for_each_run(data_trial):
    grouped_trial_type_new = data_trial.loc[:, [
        'run_id', 'chinFirst', 'trial_index',
        'trial_type', 'trial_type_new']] \
        .drop_duplicates()

    last_trial_for_each_run = data_trial \
        .groupby(['run_id'])['trial_index'].max() \
        .reset_index() \
        .merge(grouped_trial_type_new,
               on=['run_id', 'trial_index'],
               how='left')

    last_trial_for_each_run = add_next_trial(
        last_trial_for_each_run, data_trial)

    return last_trial_for_each_run


def dropout_by_type(data_trial):

    max_trial_by_run = data_trial \
        .groupby(['run_id'], as_index=False).agg(
            trial_index=('trial_index', 'max')) \
        .merge(
            data_trial[['run_id', 'trial_index',
                        'chinFirst', 'prolificID',
                        'trial_type_new', 'status']],
            on=['run_id', 'trial_index'],
            how='left')

    max_trial_by_run = add_next_trial(max_trial_by_run, data_trial)

    max_trial_by_type = max_trial_by_run \
        .groupby(['next_trial_type_new'], as_index=False) \
        .agg(n=('run_id', 'count')) \
        .sort_values(by='n')

    max_trial_by_type['percent'] = round(
        100 * max_trial_by_type['n'] /
        len(data_trial['run_id'].unique()), 1)

    print(f'Dropout by type: \n {max_trial_by_type} \n')

    write_csv(
        max_trial_by_type,
        'dropout_by_type.csv',
        'results', 'tables', 'dropouts')

    data_plot = max_trial_by_run[
        max_trial_by_run['next_trial_type_new'] != 'end'] \
            .groupby(
                ['next_trial_type_new'],
                as_index=False).agg(n=('run_id', 'count'))

    fig, ax = plt.subplots()
    ax.bar(data_plot['next_trial_type_new'], data_plot['n'])

    max_y = round(data_plot['n'].max() / 10) * 10
    ax.set_ylabel('Frequency')
    ax.yaxis.set_ticks(np.arange(0, max_y, 5))
    ax.set_title('Dropouts by trial type')

    fig.autofmt_xdate(rotation=45)

    plt.tight_layout()
    save_plot('dropouts.png', 'results', 'plots', 'dropouts')
    plt.close()


def check_calibration(data_trial):
    #    The last trial during calibration varies. There no one
    #    first calibration or similar, when the subjects drop out.

    grouped_trial_type_new = data_trial[[
         'run_id', 'trial_index', 'chinFirst',
         'trial_type', 'trial_type_new']] \
        .drop_duplicates()

    last_trial_for_each_subject = data_trial \
        .groupby(['run_id'])['trial_index'].max() \
        .reset_index() \
        .merge(grouped_trial_type_new,
               on=['run_id', 'trial_index'],
               how='left')

    last_trial_for_each_subject = add_next_trial(
        last_trial_for_each_subject, data_trial)

    cal_1_summary = last_trial_for_each_subject.loc[
        last_trial_for_each_subject['next_trial_type_new'] == 'calibration_1',
        [
            'run_id', 'trial_index', 'chinFirst', 'trial_type_new',
            'next_trial_type_new', 'next_trial_type']
    ]
    print(f"""Dropouts during calibration 1: \n {cal_1_summary} \n""")

    write_csv(
        cal_1_summary,
        'dropouts_cal_1.csv',
        'results', 'tables', 'dropouts')


def multi_participation_by_run(data_trial):
    """
        Check, how participants try again and how many only try once
    :param data_trial:
    :return:
    """

    max_trial_by_run = data_trial \
        .groupby(['run_id'], as_index=False).agg(
            max_trial=('trial_index', 'max')) \
        .merge(
            data_trial[['run_id', 'trial_index', 'prolificID',
                        'trial_type_nr', 'trial_type_new', 'status']] \
                .rename(columns={'trial_index': 'max_trial'}),
            on=['run_id', 'max_trial'],
            how='left')

    attempts_by_id = max_trial_by_run \
        .groupby(['prolificID'], as_index=False).agg(
            n=('run_id', 'count'),
            status=('status', 'unique'))

    ids_one_attempt = attempts_by_id.loc[
        attempts_by_id['n'] < 2, 'prolificID'].unique()
    ids_multiple_attempts = attempts_by_id.loc[
        attempts_by_id['n'] > 1, 'prolificID'].unique()

    summary = pd.DataFrame({
        'name': [
            'ids_one_attempt',
            'ids_multiple_attempts'],
        'length': [
            len(ids_one_attempt),
            len(ids_multiple_attempts)],
        'percentage (resp.)': [
            len(ids_one_attempt) / len(data_trial['prolificID'].unique()),
            len(ids_multiple_attempts) / len(data_trial['prolificID'].unique())],
    })

    print(f"""attempts_by_id: \n{attempts_by_id['n'].describe()} \n"""
          f"""{summary}\n""")

    return ids_one_attempt, ids_multiple_attempts


def multi_participation_by_type(data_trial):
    """
        When do the participants stop and go back?
        Most of the participants, who try again, reload at the
        beginning of the experiment.
    """
    duplicate_subjects = data_trial \
                             .loc[:, ['prolificID', 'run_id']] \
        .drop_duplicates() \
        .groupby(['prolificID'], as_index=False)['run_id'].count() \
        .rename(columns={'run_id': 'n'})
    duplicate_subjects = duplicate_subjects \
        .loc[duplicate_subjects['n'] > 1, 'prolificID'] \
        .unique()

    runs_max_trial = data_trial.loc[data_trial['prolificID'].isin(duplicate_subjects), :] \
        .groupby(['prolificID', 'run_id'], as_index=False)['trial_index'].max() \
        .merge(
            data_trial[['run_id', 'chinFirst', 'trial_index',
                        'trial_type', 'trial_type_nr', 'trial_type_new']],
            on=['run_id', 'trial_index'],
            how='left')
    runs_max_trial = runs_max_trial.loc[
        runs_max_trial['trial_type_new'] != 'end', :]

    runs_max_trial = add_next_trial(runs_max_trial, data_trial)

    output = runs_max_trial \
        .groupby(['next_trial_type_new']).nunique()['prolificID'] \
        .reset_index() \
        .sort_values(by='prolificID')
    print(
        f"""Those with multiple attempts previously dropped out at: \n"""
        f"""{output} \n""")

    write_csv(
        output,
        'multi_participation_trial_type.csv',
        'results', 'tables', 'dropouts')
