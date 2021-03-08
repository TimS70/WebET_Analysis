import os

import numpy as np
import pandas as pd

from data_prep.screening_and_cleaning.invalid_runs \
    import filter_runs_low_fps
from utils.data_frames import add_var_to_data_et
from utils.path import makedir
from utils.tables import summarize_datasets


def clean_choice_data():
    print('Cleaning choice data... \n')
    data_et = pd.read_csv(
        os.path.join('data', 'cleaned', 'data_et.csv'))
    data_trial = pd.read_csv(
        os.path.join('data', 'cleaned', 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join('data', 'cleaned', 'data_subject.csv'))
    print('Imported from data/cleaned: ')
    summarize_datasets(data_et, data_trial, data_subject)

    data_trial = select_choice_columns(data_trial)
    data_et = filter_et_choice(data_et, data_trial)

    # Screening
    show_slow_reaction_times(data_trial)
    invalid_runs = invalid_choice_runs(data_trial, data_et)

    data_subject = data_subject.loc[
                   ~data_subject['run_id'].isin(invalid_runs), :]

    print('Cleaning trials: \n')
    data_trial = clean_choice_trial_data(
        data_trial, 'data_trial', invalid_runs)
    data_et = add_var_to_data_et(
        data_et, data_trial, 'trial_duration_exact')
    data_et = clean_choice_trial_data(
        data_et, 'data_et', invalid_runs)
    data_et = data_et.drop(columns='trial_duration_exact')

    data_et = clean_et_choice_data(
        data_et, invalid_runs)

    makedir('data', 'choice_task', 'cleaned')
    data_et.to_csv(
        os.path.join('data', 'choice_task', 'cleaned', 'data_et.csv'),
        index=False, header=True)
    data_trial.to_csv(
        os.path.join('data', 'choice_task', 'cleaned', 'data_trial.csv'),
        index=False, header=True)
    data_subject.to_csv(
        os.path.join('data', 'choice_task', 'cleaned', 'data_subject.csv'),
        index=False, header=True)
    print(data_trial.columns)
    summarize_datasets(data_et, data_trial, data_subject)

    check_unequal_trial_numbers(data_et, data_trial)


def select_choice_columns(data_trial):
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


def filter_et_choice(data_et, data_trial):
    data_et = add_var_to_data_et(data_et, data_trial, 'trial_type')
    data_et = add_var_to_data_et(data_et, data_trial, 'withinTaskIndex')

    data_et = data_et.loc[
              data_et['trial_type'] == 'eyetracking-choice', :] \
        .drop(columns=['trial_type'])
    data_et = data_et.loc[:, [
                  'run_id', 'trial_index', 'withinTaskIndex',
                  'x', 'y', 't_task']
              ]

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

    print(
        f"""Average reaction time below 10 seconds: \n"""
        f"""M = {round(m_below_10, 2)}, """
        f"""SD = {round(sd_below_10, 2)} \n"""
    )


def invalid_choice_runs(data_trial, data_et):
    runs_low_fps = filter_runs_low_fps(data_trial, data_et, 10)
    # Run 144 was found to barely have any variation in
    # gaze transitions
    runs_additional_flaws = np.array([144])

    invalid_runs = list(
        set(runs_low_fps) |
        set(runs_additional_flaws)
    )

    summary_output = pd.DataFrame(
        {'name': [
            'subjects_lowFPS',
            'additional_flaws',
            'total',
        ],
            'length': [
                len(runs_low_fps),
                len(runs_additional_flaws),
                len(invalid_runs)
            ]}
    )

    print(
        f"""Invalid runs for choice task: \n"""
        f"""{summary_output} \n""")

    return invalid_runs


def clean_choice_trial_data(data, name, invalid_runs):

    data_raw = data
    data = data_raw.loc[
           ~(data_raw['run_id'].isin(invalid_runs)) &
           (data_raw['trial_duration_exact'] < 10000),
           :]

    print(
        f"""{name}: Removing invalid runs and long trials (>10s) \n"""
        f"""Raw: {len(data_raw)} \n"""
        f"""Cleaned: {len(data)} \n""")

    return data


def clean_et_choice_data(data, invalid_runs):

    data_raw = data
    data = data_raw.loc[
           (data_raw['x'] > 0) & (data_raw['x'] < 1) &
           (data_raw['y'] > 0) & (data_raw['y'] < 1) &
           ~(data_raw['run_id'].isin(invalid_runs)),
           :]

    print(
        f"""data_et: Filter gaze points on the screen: \n"""
        f"""Raw: {len(data_raw)} \n"""
        f"""Cleaned: {len(data)} \n""")


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

    print(
        f"""{len(grouped_missing_et)} runs have at least one """
        f"""empty (et-related) trial. \n"""
        f"""That is where the difference of """
        f"""{grouped_missing_et['trial_index'].sum()} trials """
        f"""is coming from."""
    )
    print(grouped_missing_et)
