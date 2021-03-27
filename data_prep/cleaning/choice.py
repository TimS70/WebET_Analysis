import os

import numpy as np
import pandas as pd

from data_prep.cleaning.find_invalid_runs.invalid_runs \
    import filter_runs_low_fps, clean_runs
from utils.data_frames import merge_by_index
from utils.tables import load_all_three_datasets, save_all_three_datasets, write_csv


def create_choice_data():
    print('################################### \n'
          'Create choice data \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'all_trials', 'cleaned'))

    data_trial = init_choice_data_trial(data_trial)
    data_et = init_choice_data_et(data_et, data_trial)

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'choice_task', 'raw'))


def clean_choice_data():
    print('################################### \n'
          'Clean choice data \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'choice_task', 'added_var'))

    # Screening
    show_slow_reaction_times(data_trial)
    invalid_runs = invalid_runs_choice(data_trial, data_et, data_subject)

    # Remove invalid runs
    data_subject = clean_runs(data_subject, invalid_runs, 'data_subject')
    data_trial = clean_runs(data_trial, invalid_runs, 'data_trial')
    data_et = clean_runs(data_et, invalid_runs, 'data_et')

    # Remove Long trials
    data_trial = clean_trial_duration(data_trial, 400, 10000, 'data_trial')

    data_et = merge_by_index(data_et, data_trial, 'trial_duration_exact')
    data_et = clean_trial_duration(data_et, 400, 10000, 'data_et')
    data_et = data_et.drop(columns='trial_duration_exact')

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'choice_task', 'cleaned'))

    check_unequal_trial_numbers(data_et, data_trial)


def init_choice_data_trial(data_trial):
    data_trial = data_trial.loc[
        data_trial['trial_type'] == 'eyetracking-choice',
        [
            'run_id', 'prolificID', 'chinFirst',
            'task_nr',
            'trial_index', 'trial_type', 'withinTaskIndex',
            'choiceTask_amountLeftFirst',
            'option_topLeft', 'option_bottomLeft',
            'option_topRight', 'option_bottomRight',
            'key_press', 'trial_duration_exact',
            'window_width', 'window_height',
            'fps'
        ]
    ]

    return data_trial


def init_choice_data_et(data_et, data_trial):
    data_et = merge_by_index(data_et, data_trial, 'trial_type')
    data_et = merge_by_index(data_et, data_trial, 'withinTaskIndex')

    data_et = data_et.loc[
              data_et['trial_type'] == 'eyetracking-choice', :] \
        .drop(columns=['trial_type'])
    data_et = data_et.loc[:, [
                                 'run_id', 'trial_index', 'withinTaskIndex',
                                 'x', 'y', 't_task']]

    return data_et


def show_slow_reaction_times(data_trial):
    runs_slow = len(data_trial.loc[
                        data_trial['trial_duration_exact'] > 10000, 'run_id'].unique())
    print(f'Runs with slow reaction times (<10s): n = {runs_slow} \n')

    print(
        f"""Average reaction time raw: \n"""
        f"""M = {round(data_trial['trial_duration_exact'].mean(), 2)}, """
        f"""SD = {round(data_trial['trial_duration_exact'].std(), 2)} \n"""
    )

    m_below_10 = data_trial.loc[
        data_trial['trial_duration_exact'] < 10000,
        'trial_duration_exact'].mean()

    sd_below_10 = data_trial.loc[
        data_trial['trial_duration_exact'] < 10000,
        'trial_duration_exact'].std()

    print(f"""Average reaction time below 10 seconds: \n"""
          f"""M = {round(m_below_10, 2)}, """
          f"""SD = {round(sd_below_10, 2)} \n""")


def filter_hit_ratio(data_subject, min_hit_ratio=0.8):
    runs_low_hit_ratio = data_subject.loc[
        data_subject['hit_ratio'] > min_hit_ratio,
        'run_id']

    return runs_low_hit_ratio


def clean_trial_duration(data_raw, min_time, max_time, name):
    data = data_raw[
        (data_raw['trial_duration_exact'] > min_time) &
        (data_raw['trial_duration_exact'] < max_time)]

    print(
        f"""Filter reaction time ({min_time} < t < {max_time}) from {name}: \n"""
        f"""   Raw: {len(data_raw)} \n"""
        f"""   Cleaned: {len(data)} \n""")

    return data


def check_unequal_trial_numbers(data_et, data_trial):
    et_trials = data_et.groupby(
        ['run_id', 'trial_index'],
        as_index=False)['x'].count() \
        .rename(columns={'x': 'x_count_2'})

    data_trial_added_count_2 = data_trial.merge(
        et_trials, on=['run_id', 'trial_index'], how='left')

    grouped_missing_et = data_trial_added_count_2.loc[
                         pd.isna(data_trial_added_count_2['x_count_2']), :] \
        .groupby(['run_id'], as_index=False)['trial_index'].count()

    if len(grouped_missing_et) > 0:
        print(f"""{len(grouped_missing_et)} runs have at least one """
              f"""empty (et-related) trial. \n"""
              f"""That is where the difference of """
              f"""{grouped_missing_et['trial_index'].sum()} trials """
              f"""is coming from: \n"""
              f"""{grouped_missing_et} \n""")
    else:
        print('No difference in trial number found')
