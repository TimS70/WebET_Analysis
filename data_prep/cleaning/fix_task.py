import os

import pandas as pd

from data_prep.cleaning.invalid_runs import clean_runs
from utils.data_frames import merge_by_index
from utils.path import makedir
from utils.tables import summarize_datasets


def clean_fix_task_datasets():
    data_et = pd.read_csv(
        os.path.join('data', 'fix_task', 'raw', 'data_et.csv'))
    data_et_fix = pd.read_csv(
        os.path.join('data', 'fix_task', 'raw', 'data_et_fix.csv'))
    data_trial = pd.read_csv(
        os.path.join('data', 'fix_task', 'raw', 'data_trial.csv'))
    data_trial_fix = pd.read_csv(
        os.path.join('data', 'fix_task', 'raw', 'data_trial_fix.csv'))
    data_subject = pd.read_csv(
        os.path.join('data', 'fix_task', 'raw', 'data_subject.csv'))

    print('Datasets read from data/fix_task/raw (fix task trials): ')
    summarize_datasets(data_et_fix, data_trial_fix, data_subject)

    print('Datasets read from data/fix_task/raw (all trials): ')
    summarize_datasets(data_et, data_trial, data_subject)


    # Screening
    invalid_runs = screen_fix_task(data_trial_fix, data_subject)

    data_trial = clean_runs(data_trial, invalid_runs, 'data_trial')
    data_et = clean_runs(data_et, invalid_runs, 'data_et')
    data_trial_fix = clean_runs(data_trial_fix, invalid_runs, 'data_trial_fix')
    data_et_fix = clean_runs(data_et_fix, invalid_runs, 'data_et_fix')
    data_subject = clean_runs(data_subject, invalid_runs, 'data_subject')

    data_trial = remove_high_tTask(data_trial, 'data_trial')
    data_et = remove_high_tTask(data_et, 'data_et')
    data_trial_fix = remove_high_tTask(data_trial_fix, 'data_trial_fix')
    data_et_fix = remove_high_tTask(data_et_fix, 'data_et_fix')

    data_trial_fix = data_trial_fix.loc[
                     pd.notna(data_trial_fix['x_count']), :]

    makedir('data', 'fix_task', 'cleaned')
    data_et.to_csv(
        os.path.join('data', 'fix_task', 'cleaned', 'data_et.csv'),
        index=False, header=True)
    data_et_fix.to_csv(
        os.path.join('data', 'fix_task', 'cleaned', 'data_et_fix.csv'),
        index=False, header=True)
    data_trial.to_csv(
        os.path.join('data', 'fix_task', 'cleaned', 'data_trial.csv'),
        index=False, header=True)
    data_trial_fix.to_csv(
        os.path.join('data', 'fix_task', 'cleaned', 'data_trial_fix.csv'),
        index=False, header=True)
    data_subject.to_csv(
        os.path.join('data', 'fix_task', 'cleaned', 'data_subject.csv'),
        index=False, header=True)
    print('Datasets saved to data/fix_task/cleaned: ')
    summarize_datasets(data_et_fix, data_trial_fix, data_subject)


def screen_fix_task(data_trial_fix, data_subject):
    show_empty_fix_trials(data_trial_fix)
    show_trials_high_t_task(data_trial_fix, max_t_task=5500)

    runs_incomplete_fix_task = runs_with_incomplete_fix_tasks(
        data_trial_fix)
    runs_bad_time_measure = runs_long_trials(
        data_trial_fix, max_t_task=5500)
    runs_na_glasses = missing_glasses(data_subject)

    invalid_runs = list(
        set(runs_incomplete_fix_task) |
        set(runs_bad_time_measure) |
        set(runs_na_glasses)
    )

    summary = pd.DataFrame(
        {'name': [
            'subjects_NA_glasses',
            'subjects_bad_time_measure',
            'subjects_incomplete_fix',
            'total'
        ],
            'length': [
                len(runs_incomplete_fix_task),
                len(runs_bad_time_measure),
                len(runs_na_glasses),
                len(invalid_runs)
            ]}
    )

    print(
        f"""Invalid runs for fix task: \n"""
        f"""{summary} \n"""
    )

    return invalid_runs


def show_empty_fix_trials(data_trial_fix):
    null_data = data_trial_fix.loc[pd.isna(data_trial_fix['x_count']), :]

    print(
        f"""N fixation trials with no et_data: n = {len(null_data)}""")
    if len(null_data) > 0:
        print(f"""{null_data} \n""")


def show_trials_high_t_task(data_trial_fix, max_t_task):
    grouped_time_by_trial = data_trial_fix.loc[
                            data_trial_fix['trial_duration_exact'] > max_t_task, :] \
                                .groupby(['run_id', 'trial_index']).mean() \
                                .reset_index() \
                                .loc[:, ['run_id', 'trial_index', 'trial_duration_exact']]
    print(
        f"""Number of very long trials grouped_time_by_trial: """
        f"""{len(grouped_time_by_trial)} \n"""
        f"""{grouped_time_by_trial} \n"""
    )


def runs_with_incomplete_fix_tasks(data_trial_fix):
    n_trials_by_run = data_trial_fix \
        .groupby(['run_id'], as_index=False)['trial_index'].count() \
        .rename(columns={'trial_index': 'n'})

    runs_incomplete_fix_task = n_trials_by_run.loc[
        n_trials_by_run['n'] < 18, 'run_id']

    summary = n_trials_by_run.loc[
              n_trials_by_run['run_id'].isin(runs_incomplete_fix_task),
              :]
    print(
        f"""Incomplete runs with number of trials: \n"""
        f"""{summary} \n"""
    )

    return runs_incomplete_fix_task


def runs_long_trials(data_trial_fix, max_t_task):
    grouped_time_by_trial = data_trial_fix.loc[
                            data_trial_fix['trial_duration_exact'] > max_t_task, :] \
                                .groupby(['run_id', 'trial_index']).mean() \
                                .reset_index() \
                                .loc[:, ['run_id', 'trial_index', 'trial_duration_exact']]

    runs_with_long_trials = grouped_time_by_trial \
        .groupby(['run_id'], as_index=False)['trial_index'].count() \
        .rename(columns={'trial_index': 'n'}) \
        .sort_values(by='n')

    runs_bad_time_measure = runs_with_long_trials.loc[
        runs_with_long_trials['n'] > 3,
        'run_id']

    summary = grouped_time_by_trial.loc[
              grouped_time_by_trial['run_id'].isin(runs_bad_time_measure),
              :]

    print(
        f"""Runs with long trials: \n"""
        f"""{summary} \n""")

    return runs_bad_time_measure


def missing_glasses(data_subject):
    runs_na_glasses = data_subject.loc[
        pd.isna(data_subject['glasses_binary']),
        'run_id']

    print(
        f"""n={len(runs_na_glasses)} """
        f"""participants were excluded because we did not provide """
        f"""information about their sight. \n""")

    return runs_na_glasses


def remove_high_tTask(data, name):
    data_raw = data

    data = data_raw.loc[data_raw['trial_duration_exact'] <= 5500, :]

    print(
        f"""Removing trials that were too long from {name}: \n"""
        f"""Raw: {len(data_raw['run_id'].unique())} \n"""
        f"""Cleaned: {len(data['run_id'].unique())} \n""")

    return data
