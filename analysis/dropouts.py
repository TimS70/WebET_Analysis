import os

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from data_prep.screening_and_cleaning.filter_approved import filter_approved


def dropout_analysis():

    data_trial = pd.read_csv(
        os.path.join('data', 'added_var', 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join('data', 'added_var', 'data_subject.csv'))

    data_trial = filter_approved(data_trial, data_subject)
    data_subject = filter_approved(d, data_subject)

    dropout_by_task_nr(data_trial)
    how_many_runs_with_dropouts(data_trial)

    last_trial_for_each_run = group_last_trial_for_each_run(data_trial)
    group_dropout_by_type(data_trial)
    check_calibration(data_trial)
    check_multi_participation(data_trial)



def dropout_by_task_nr(data):
    grouped_trial_type_new = data.loc[
        :, ['run_id', 'trial_index', 'task_nr_new']] \
        .drop_duplicates()

    last_trial_for_each_subject = data.groupby(['run_id'])['trial_index'].max() \
        .reset_index() \
        .merge(grouped_trial_type_new, on=['run_id', 'trial_index'], how='left') \
        .loc[:, ['run_id', 'task_nr_new']]

    dropout_by_type = last_trial_for_each_subject \
        .groupby(['task_nr_new'])['run_id'].count() \
        .reset_index() \
        .rename(columns={'run_id': 'n_run_id'}) \
        .sort_values(by='n_run_id')

    return dropout_by_type


def how_many_runs_with_dropouts(data_trial):
    grouped_last_trial = data_trial.groupby(['run_id'])['trial_index'].max() \
        .reset_index() \
        .merge(
        data_trial.loc[
        :, [
               'run_id', 'trial_index', 'prolificID',
               'trial_type_nr', 'trial_type_new']],
        on=['run_id', 'trial_index'],
        how='left'
    )

    grouped_last_trial_dropout = grouped_last_trial.loc[
                                 grouped_last_trial['trial_type_new'] != 'end',
                                 :
                                 ]

    runs_dropout = grouped_last_trial_dropout['run_id']

    dropout_rate = len(runs_dropout) / len(data_trial['run_id'].unique())
    print(
        f"""N Runs with dropout: n={len(runs_dropout)}"""
        f""" = {round(100 * dropout_rate, 2)}%""")

    data = grouped_last_trial_dropout \
        .groupby(
            ['trial_type_nr', 'trial_type_new'],
            as_index=False)['run_id'].count() \
        .rename(columns={'run_id': 'n'})

    fig, ax = plt.subplots()
    ax.bar(data['trial_type_new'], data['n'])

    for ax in fig.axes:
        ax.tick_params(labelrotation=90)


def group_last_trial_for_each_run(data_trial):
    grouped_trial_type_new = data_trial \
                                 .loc[:, ['run_id', 'chinFirst', 'trial_index', 'trial_type_new']] \
        .drop_duplicates()

    last_trial_for_each_run = data_trial \
        .groupby(['run_id'])['trial_index'].max() \
        .reset_index() \
        .merge(grouped_trial_type_new, on=['run_id', 'trial_index'], how='left')

    last_trial_for_each_run = add_next_trial(last_trial_for_each_run)
    return last_trial_for_each_run


def group_dropout_by_type(data_trial):
    """
        Most runs drop out at the beginning (8.8% chinFirst +7.2% no chinFirst),
        in detail, during the initialization of Webgazer (4.4%+3.2%), during the
        calibration instruction (0.6%+2.5%) and the calibration itself (1.2+0.3%).
        Moreover, some dropouts during the tasks (0.6+1.8%).

    :param data_trial:
    :return:
    """
    last_trial_for_each_run = group_last_trial_for_each_run(data_trial)
    dropout_by_type = last_trial_for_each_run \
        .groupby(['trial_type_new', 'next_trial_type_new', 'next_trial_type']).count() \
        .reset_index() \
        .rename(columns={'run_id': 'n_run_id'}) \
        .loc[:, ['trial_type_new', 'next_trial_type_new',
                 'next_trial_type', 'n_run_id']] \
        .sort_values(by='n_run_id')

    dropout_by_type['perc'] = round(
        100 * dropout_by_type['n_run_id'] / len(data_trial['run_id'].unique()),
        1
    )

    print(f'Dropout by_type \n {dropout_by_type}')

    summary = pd.DataFrame([
        [
            'beginning',
            sum(
                dropout_by_type.loc[
                    dropout_by_type['next_trial_type_new'].isin([
                        'pre_et_init',
                        'et_init',
                        'et_adjustment',
                        'calibration_1_briefing',
                        'calibration_1',
                    ]),
                    'n_run_id']),
            sum(dropout_by_type.loc[
                    dropout_by_type['next_trial_type_new'].isin([
                        'pre_et_init',
                        'et_init',
                        'et_adjustment',
                        'calibration_1_briefing',
                        'calibration_1',
                    ]),
                    'perc'])
        ],
        [
            'et_tasks',
            sum(dropout_by_type.loc[
                    dropout_by_type['next_trial_type_new'].isin([
                        'fixation_1',
                        'fixation_2',
                        'calibration_2',
                        'choice',
                    ]),
                    'n_run_id']),
            sum(dropout_by_type.loc[
                    dropout_by_type['next_trial_type_new'].isin([
                        'fixation_1',
                        'fixation_2',
                        'calibration_2',
                        'choice',
                    ]),
                    'perc'])
        ],
        [
            'total',
            sum(dropout_by_type['n_run_id']),
            sum(dropout_by_type['perc'])
        ]
    ], columns=['type', 'sum', 'perc'])

    print(summary)

    return dropout_by_type


def add_next_trial(data):
    full_trials_no_chin = data.loc[
        data['run_id'] == 421,
        ['trial_index', 'trial_type', 'trial_type_new']
    ].reset_index(drop=True)

    next_trials_no_chin = full_trials_no_chin
    next_trials_no_chin['trial_index'] -= 1

    full_trials_chin = data.loc[
        data['run_id'] == 270,
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
            next_trials = next_trials_chin if data.loc[i, 'chinFirst'] > 0 else next_trials_no_chin

            next_trial = next_trials.loc[
                next_trials['trial_index'] == this_trial,
                'trial_type'
            ].values[0]
            data.loc[i, 'next_trial_type'] = next_trial

            next_trial = next_trials.loc[
                next_trials['trial_index'] == this_trial,
                'trial_type_new'
            ].values[0]
            data.loc[i, 'next_trial_type_new'] = next_trial

        else:
            data.loc[i, 'next_trial_type'] = 'end'
            data.loc[i, 'next_trial_type_new'] = 'end'

    return data


def check_calibration(data_trial):

    #    The last trial during calibration varies. There no one
    #    first calibration or similar, when the subjects drop out.

   grouped_trial_type_new = data_trial \
        .loc[:, ['run_id', 'trial_index', 'chinFirst', 'trial_type_new']] \
        .drop_duplicates()

   last_trial_for_each_subject = data_trial \
        .groupby(['run_id'])['trial_index'].max() \
        .reset_index() \
        .merge(grouped_trial_type_new, on=['run_id', 'trial_index'], how='left')

   last_trial_for_each_subject = add_next_trial(last_trial_for_each_subject)

   cal_1_summary = last_trial_for_each_subject.loc[
        last_trial_for_each_subject['next_trial_type_new'] == 'calibration_1',
        [
            'run_id', 'trial_index', 'chinFirst', 'trial_type_new',
            'next_trial_type_new', 'next_trial_type']
    ]
   print(cal_1_summary)


def check_multi_participation(data_trial):
    """:cvar
        Most subjects, who had to redo, previously dropped out during
        calibration briefing (n=7) and the initialization (n=11) multiple times
    """

    muli_participations_by_run(data_trial)
    multi_participation_by_trial_type(data_trial)


def muli_participations_by_run(data_trial):
    grouped_last_trial = data_trial.groupby(['run_id'])['trial_index'].max() \
        .reset_index() \
        .merge(
        data_trial.loc[
        :, [
               'run_id', 'trial_index', 'prolificID',
               'trial_type_nr', 'trial_type_new']],
        on=['run_id', 'trial_index'],
        how='left'
    )

    grouped_last_trial_dropout = grouped_last_trial.loc[
         grouped_last_trial['trial_type_new'] != 'end', :]

    grouped_last_trial = data_trial.groupby(['run_id'])['trial_index'].max() \
        .reset_index() \
        .merge(
        data_trial.loc[
        :, [
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
        'prolificID'
    ].unique():
        previous_attempt = grouped_last_trial_full.loc[
                           grouped_last_trial_full['prolificID'] == ID,
                           :
                           ]
        if len(previous_attempt) > 0:
            subjects_multiple_attempts = np.append(
                subjects_multiple_attempts, ID)
        else:
            subjects_actual_dropouts = np.append(
                subjects_actual_dropouts, ID)

    prolific_ids = data_trial['prolific'].unique()
    multi_attempts_rate = len(subjects_multiple_attempts) / len(prolific_ids)
    actual_dropout_rate = len(subjects_actual_dropouts) / len(prolific_ids)

    print(
        f"""Of those subjects where the ID is known: n={len(prolific_ids)}\n"""
        f"""Subjects_multiple_attempts: n={len(subjects_multiple_attempts)}"""
        f""" = {round(100 * multi_attempts_rate, 2)}% \n"""
        f"""subjects_actual_dropouts: n={len(subjects_actual_dropouts)}"""
        f""" = {round(100 * actual_dropout_rate, 2)}% \n"""
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
            data_trial.loc[:,[
                'run_id', 'chinFirst', 'trial_index',
                'trial_type', 'trial_type_nr', 'trial_type_new']],
        on=['run_id', 'trial_index'],
        how='left')
    runs_max_trial = runs_max_trial \
                         .loc[runs_max_trial['trial_type_new'] != 'end', :]

    runs_max_trial = add_next_trial(runs_max_trial)

    output = runs_max_trial \
        .groupby(['next_trial_type_new']).nunique()['prolificID'] \
        .reset_index() \
        .sort_values(by='prolificID')
    print(output)
