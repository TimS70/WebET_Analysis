import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data_prep.cleaning.invalid_runs import clean_runs
from utils.plots import save_plot
from utils.tables import write_csv


def dropout_analysis():

    print('################################### \n'
          'Analyze dropouts \n'
          '################################### \n')

    data_trial = pd.read_csv(
        os.path.join('data', 'all_trials', 'added_var', 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join('data', 'all_trials', 'added_var', 'data_subject.csv'))

    # Filter those from prolific
    data_subject = data_subject.loc[
                   pd.notna(data_subject['prolificID']), :]
    data_trial = data_trial.loc[
        data_trial['run_id'].isin(data_subject['run_id']), :]

    data_not_approved = data_subject.loc[
        (data_subject['status'] != 'APPROVED') &
        ~(data_subject['run_id'].isin(data_trial['run_id'])),
        [
            'run_id', 'prolificID', 'max_trial',
            'recorded_date', 'status'
        ]]

    total_ids = data_subject['prolificID'].unique()
    ids_not_approved = data_not_approved['prolificID'].unique()
    rate_not_approved = len(ids_not_approved) / len(total_ids)

    print(
        f"""Not approved participants who did not start the study: \n"""
        f"""total: {len(ids_not_approved)} of """
        f"""{len(total_ids)} ({rate_not_approved}) \n"""
        f"""nan:   {sum(pd.isna(data_subject['status']))} \n"""
        f"""{pd.crosstab(index=data_not_approved['status'], columns="n")} \n"""
    )

    # Filter those who have trials
    data_subject = data_subject.loc[
                   data_subject['run_id'].isin(data_trial['run_id']), :]

    print(
        f"""Unique ID's who actually have some trials: \n"""
        f"""   data_subject: {len(data_subject['prolificID'].unique())}\n"""
        f"""   data_trial:   {len(data_trial['prolificID'].unique())}\n"""
    )

    data_not_approved = data_subject.loc[
        data_subject['status'] != 'APPROVED',
        [
            'run_id', 'prolificID', 'max_trial',
            'recorded_date', 'status'
        ]]

    print(
        f"""not approved participants who started the trial: \n"""
        f"""total: {len(data_not_approved['prolificID'].unique())} of """
        f"""{len(data_subject['prolificID'].unique())} """
        f"""participants \n"""
        f"""nan:   {sum(pd.isna(data_subject['status']))} \n"""
        f"""{pd.crosstab(index=data_not_approved['status'], columns="n")} \n"""
    )

    how_many_runs_with_dropouts(data_trial)
    dropout_by_task_nr(data_trial)

    group_dropout_by_type(data_trial)
    check_calibration(data_trial)
    check_multi_participation(data_trial)


def how_many_runs_with_dropouts(data_trial):
    grouped_last_trial = data_trial.groupby(['run_id'])['trial_index'].max() \
        .reset_index() \
        .merge(
        data_trial.loc[:, [
               'run_id', 'trial_index', 'prolificID',
               'trial_type_nr', 'trial_type_new']],
        on=['run_id', 'trial_index'],
        how='left'
    )

    grouped_last_trial_dropout = grouped_last_trial.loc[
                                 grouped_last_trial['trial_type_new'] != 'end',
                                 :]

    runs_dropout = grouped_last_trial_dropout['run_id']

    dropout_rate = len(runs_dropout) / len(data_trial['run_id'].unique())
    print(
        f"""N Runs with dropout: n={len(runs_dropout)}"""
        f""" = {round(100 * dropout_rate, 2)}% \n""")

    data = grouped_last_trial_dropout \
        .groupby(
            ['trial_type_nr', 'trial_type_new'],
            as_index=False)['run_id'].count() \
        .rename(columns={'run_id': 'n'})

    fig, ax = plt.subplots()
    ax.bar(data['trial_type_new'], data['n'])

    max_y = round(data['n'].max()/10)*10
    ax.set_ylabel('Frequency')
    ax.yaxis.set_ticks(np.arange(0, max_y, 5))
    ax.set_title('Dropouts by trial type')

    fig.autofmt_xdate(rotation=45)

    plt.tight_layout()
    save_plot('dropouts.png', 'results', 'plots', 'dropouts')

    plt.close()


def dropout_by_task_nr(data):
    grouped_trial_type_new = data.loc[:, [
                                             'run_id',
                                             'trial_index',
                                             'task_nr_new']] \
        .drop_duplicates()

    last_trial_for_each_subject = data.groupby(
            ['run_id'],
            as_index=False)['trial_index'].max() \
        .merge(
            grouped_trial_type_new,
            on=['run_id', 'trial_index'],
            how='left') \
        .loc[:, ['run_id', 'task_nr_new']]

    output = last_trial_for_each_subject \
        .groupby(
            ['task_nr_new'],
            as_index=False)['run_id'].count() \
        .rename(columns={'run_id': 'n_run_id'}) \
        .sort_values(by='n_run_id')

    print(
        f"""Dropout by task nr: \n"""
        f"""{output} \n"""
    )

    write_csv(
        output,
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


def group_dropout_by_type(data_trial):

    last_trial_for_each_run = group_last_trial_for_each_run(data_trial)
    dropout_by_type = last_trial_for_each_run.groupby(
            ['trial_type_new', 'next_trial_type_new',
             'next_trial_type'],
            as_index=False).count() \
        .rename(columns={'run_id': 'n_run_id'}) \
        .loc[:, ['trial_type_new', 'next_trial_type_new',
               'next_trial_type', 'n_run_id']] \
        .sort_values(by='n_run_id')

    dropout_by_type['percent'] = round(
        100 * dropout_by_type['n_run_id'] / len(data_trial['run_id'].unique()),
        1
    )

    print(f'Dropout by type: \n {dropout_by_type} \n')

    write_csv(
        dropout_by_type,
        'dropout_by_type.csv',
        'results', 'tables', 'dropouts')

    return dropout_by_type


def add_next_trial(data, data_trial):
    full_trials_no_chin = data_trial.loc[
        data_trial['run_id'] == 421,
        ['trial_index', 'trial_type', 'trial_type_new']
    ].reset_index(drop=True)

    next_trials_no_chin = full_trials_no_chin
    next_trials_no_chin['trial_index'] -= 1

    full_trials_chin = data_trial.loc[
        data_trial['run_id'] == 270,
        ['trial_index', 'trial_type', 'trial_type_new']
    ].reset_index(drop=True)

    next_trials_chin = full_trials_chin
    next_trials_chin['trial_index'] -= 1

    data = data.copy()
    data['next_trial_type'] = 0
    data['next_trial_type_new'] = 0

    for i in data.index:
        this_trial = data.loc[i, 'trial_index']

        if data.loc[i, 'trial_type_new'] != 'end':
            if this_trial > 0:
                next_trials = next_trials_chin \
                    if data.loc[i, 'chinFirst'] > 0 \
                    else next_trials_no_chin

                next_trial_type = next_trials.loc[
                    next_trials['trial_index'] == this_trial,
                    'trial_type'].values[0]

                next_trial_type_new = next_trials.loc[
                    next_trials['trial_index'] == this_trial,
                    'trial_type_new'].values[0]

            else:
                next_trial_type = np.nan
                next_trial_type_new = np.nan

            data.loc[i, 'next_trial_type'] = next_trial_type
            data.loc[i, 'next_trial_type_new'] = next_trial_type_new

        else:
            data.loc[i, 'next_trial_type'] = 'end'
            data.loc[i, 'next_trial_type_new'] = 'end'

    return data


def check_calibration(data_trial):
    #    The last trial during calibration varies. There no one
    #    first calibration or similar, when the subjects drop out.

    grouped_trial_type_new = data_trial.loc[
                             :,
                             [
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


def check_multi_participation(data_trial):
    """
        Most subjects, who had to redo, previously dropped out during
        calibration briefing (n=7) and the initialization (n=11) multiple times
    """

    print('Multiple participation: ')
    multi_participation_by_run(data_trial)
    multi_participation_by_trial_type(data_trial)


def multi_participation_by_run(data_trial):
    grouped_last_trial = data_trial.groupby(['run_id'])['trial_index'].max() \
        .reset_index() \
        .merge(data_trial.loc[:, [
                   'run_id', 'trial_index', 'prolificID',
                   'trial_type_nr', 'trial_type_new']],
               on=['run_id', 'trial_index'],
               how='left')

    grouped_last_trial_dropout = grouped_last_trial.loc[
                                 grouped_last_trial['trial_type_new'] != 'end', :]

    grouped_last_trial = data_trial.groupby(['run_id'])['trial_index'].max() \
        .reset_index() \
        .merge(data_trial.loc[:, [
                   'run_id', 'trial_index', 'prolificID',
                   'trial_type_nr', 'trial_type_new']],
               on=['run_id', 'trial_index'],
               how='left')

    grouped_last_trial_full = grouped_last_trial.loc[
                              grouped_last_trial['trial_type_new'] == 'end',
                              :
                              ]

    subjects_multiple_attempts = []
    subjects_actual_dropouts = []

    for ID in grouped_last_trial_dropout.loc[
        pd.notna(grouped_last_trial_dropout['prolificID']),
        'prolificID'].unique():
        previous_attempt = grouped_last_trial_full.loc[
                           grouped_last_trial_full['prolificID'] == ID,
                           :]
        if len(previous_attempt) > 0:
            subjects_multiple_attempts = np.append(
                subjects_multiple_attempts, ID)
        else:
            subjects_actual_dropouts = np.append(
                subjects_actual_dropouts, ID)

    prolific_ids = data_trial['prolificID'].unique()
    multi_attempts_rate = len(subjects_multiple_attempts) / len(prolific_ids)
    actual_dropout_rate = len(subjects_actual_dropouts) / len(prolific_ids)

    print(
        f"""Of n={len(prolific_ids)} Prolific participants """
        f"""n={len(subjects_multiple_attempts)} participants """
        f"""({round(100 * multi_attempts_rate, 2)}%) tried again and """
        f"""n={len(subjects_actual_dropouts)} """
        f"""({round(100 * actual_dropout_rate, 2)}%) only tried once and """
        f"""then dropped out. \n"""
    )


def multi_participation_by_trial_type(data_trial):
    """
        Most of the participants, who try again, reload at the beginning of
        the experiment.
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
        data_trial.loc[:, [
                              'run_id', 'chinFirst', 'trial_index',
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
