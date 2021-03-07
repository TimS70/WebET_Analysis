import os

import numpy as np
import pandas as pd

from data_prep.screening_and_cleaning.invalid_runs \
    import filter_runs_low_fps
from utils.combine_data import add_var_to_data_et
from utils.path import makedir
from utils.tables import summarize_datasets


def clean_choice_data():
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
    data_trial = clean_choice_trial_data(data_trial, invalid_runs)

    data_et = add_var_to_data_et(
        data_et, data_trial, 'trial_duration_exact')
    data_et = clean_choice_trial_data(data_et)
    data_et = data_et.drop(columns='trial_duration_exact')
    data_et = clean_et_choice_data(data_et, invalid_runs)

    check_unequal_trial_numbers(data_et, data_trial)

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
    summarize_datasets(data_et, data_trial, data_subject)


def select_choice_columns(data_trial):
    data_trial = data_trial.loc[
        data_trial['trial_type'] == 'eyetracking-choice',
        [
            'run_id', 'chinFirst',
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

    data_et = data_et \
                  .loc[data_et['trial_type'] == 'eyetracking-choice', :] \
        .drop(columns=['trial_type'])
    data_et = data_et.loc[
              :,
              ['run_id', 'trial_index', 'withinTaskIndex', 'x', 'y', 't_task']
              ]

    return data_et


def show_slow_reaction_times(data_trial):
    print('show_slow_reaction_times: ')
    data_trial.loc[data_trial['trial_duration_exact'] > 10000, :]
    print(len(data_trial.loc[
                  data_trial['trial_duration_exact'] > 10000,
                  'run_id'
              ].unique()))

    print(
        'Average reaction time raw: ' +
        str(data_trial['trial_duration_exact'].mean()) +
        '\n SD=' +
        str(data_trial['trial_duration_exact'].std())
    )

    print(
        'Average reaction time below 10 seconds: ' +
        str(data_trial.loc[
                data_trial['trial_duration_exact'] < 10000,
                'trial_duration_exact'].mean()) +
        '\n SD=' +
        str(data_trial.loc[
                data_trial['trial_duration_exact'] < 10000,
                'trial_duration_exact'].std())
    )


def invalid_choice_runs(data_trial, data_et):
    runs_lowFPS = filter_runs_low_fps(data_trial, data_et, 10)
    # Run 144 was found to barely have any variation in
    # gaze transitions
    runs_additional_flaws = np.array([144])

    invalid_runs = list(
        set(runs_lowFPS) |
        set(runs_additional_flaws)
    )

    summary_output = pd.DataFrame(
        {'name': [
            'subjects_lowFPS',
            'assitional_flaws',
            'total',
        ],
            'length': [
                len(runs_lowFPS),
                len(runs_additional_flaws),
                len(invalid_runs)
            ]}
    )

    print(summary_output)

    return invalid_runs


def clean_choice_trial_data(data, invalid_runs):
    print('Raw: ' + str(len(data)))
    data = data.loc[
           ~(data['run_id'].isin(invalid_runs)) &
           (data['trial_duration_exact'] < 10000),
           :]
    print('Cleaned: ' + str(len(data)))
    return data


def clean_et_choice_data(data, invalid_runs):
    print('Raw: ' + str(len(data)))
    data = data.loc[
           (data['x'] > 0) & (data['x'] < 1) &
           (data['y'] > 0) & (data['y'] < 1) &
           ~(data['run_id'].isin(invalid_runs)),
           :]
    print('Cleaned: ' + str(len(data)))
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
