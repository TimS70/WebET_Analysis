import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy

from data_prep.cleaning.prolific_ids import drop_duplicate_ids
from scipy import stats
from utils.add_next_trial import add_next_trial
from utils.data_frames import merge_by_subject
from utils.inference import welch_dof, welch_ttest
from visualize.all_tasks import save_plot
from utils.tables import write_csv
from visualize.dropouts import plot_incomplete_runs


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
    ids_multiple_runs = data_trial[['prolificID', 'run_id']] \
        .drop_duplicates() \
        .groupby(['prolificID'], as_index=False) \
        .agg(n=('run_id', 'count'))

    ids_multiple_runs = ids_multiple_runs \
        .loc[ids_multiple_runs['n'] > 1, 'prolificID'] \
        .unique()

    runs_max_trial = data_trial \
        .loc[data_trial['prolificID'].isin(ids_multiple_runs), :] \
        .groupby(['prolificID', 'run_id'], as_index=False) \
        .agg(trial_index=('trial_index', 'max')) \
        .merge(
            data_trial[['run_id', 'chinFirst', 'trial_index',
                        'trial_type', 'trial_type_nr', 'trial_type_new', 'trial_duration_exact']],
            on=['run_id', 'trial_index'],
            how='left')

    runs_max_trial = add_next_trial(runs_max_trial, data_trial)

    grouped_trial_type = runs_max_trial \
        .groupby(['next_trial_type_new'], as_index=False) \
        .agg(n=('prolificID', 'nunique')) \
        .sort_values(by='n')

    print(
        f"""Those with multiple attempts previously dropped out at: \n"""
        f"""Duplicate participants: {len(ids_multiple_runs)}"""
        f"""{grouped_trial_type} \n""")

    write_csv(
        grouped_trial_type,
        'multi_participation_trial_type.csv',
        'results', 'tables', 'dropouts')

    ids_stuck_at_et_init = runs_max_trial.loc[
        runs_max_trial['next_trial_type_new'] == 'et_init', 'prolificID'] \
        .unique()

    grouped = runs_max_trial \
        .loc[
            runs_max_trial['prolificID'].isin(ids_stuck_at_et_init),
            ['prolificID', 'run_id', 'trial_index', 'next_trial_type',
             'trial_duration_exact']]

    ids_complete = grouped.loc[grouped['next_trial_type'] == 'end',
                               'prolificID'].unique()

    print(f"""Participants, who got stuck at et_index: \n"""
          f"""Total: {len(grouped['prolificID'].unique())} \n"""
          f"""N complete: {len(ids_complete)} \n"""
          f"""{grouped.set_index(['prolificID', 'run_id'])}""")


def check_et_initialization(data_subject, data_trial):
    data_trial = merge_by_subject(data_trial, data_subject, 'status')
    data_init = data_trial[data_trial['trial_type'] == 'eyetracking-init']

    grouped = data_init \
        .groupby(['status'], as_index=False) \
        .agg(
            n_runs=('run_id', 'nunique'),
            t=('trial_duration_exact', 'mean'),
            t_std=('trial_duration_exact', 'std'))

    print(f"""et_init statistics: \n"""
          f"""{grouped} \n""")

    grouped_not_approved = data_trial \
        .loc[
            (data_trial['run_id'].isin(data_init['run_id'])) &
            (data_trial['status'] != 'APPROVED'), :] \
        .groupby(['status', 'run_id'], as_index=False) \
        .agg(trial_index=('trial_index', 'max')) \
        .merge(
            data_init[['run_id', 'trial_duration_exact']],
            on='run_id',
            how='left') \
        .merge(
            data_subject[['run_id', 'fps']],
            on='run_id',
            how='left')

    print(f"""Not approved runs, et_init statistics: \n"""
          f"""{grouped_not_approved} \n""")

    # T-Tests
    print('Time')
    welch_ttest(
        data_init.loc[
            data_init['status'] == 'APPROVED', 'trial_duration_exact'].dropna(),
        data_init.loc[
            data_init['status'] == 'RETURNED', 'trial_duration_exact'].dropna())

    print('FPS')
    welch_ttest(
        data_subject.loc[data_subject['status'] == 'APPROVED', 'fps'].dropna(),
        data_subject.loc[data_subject['status'] == 'RETURNED', 'fps'].dropna())
