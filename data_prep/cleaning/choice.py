import os

import numpy as np
import pandas as pd

from data_prep.choice import add_log_k
from data_prep.cleaning.invalid_runs \
    import filter_runs_low_fps, clean_runs
from utils.data_frames import merge_by_index
from utils.path import makedir
from utils.tables import summarize_datasets


def create_choice_data():
    print('################################### \n'
          'Create choice data \n'
          '################################### \n')

    data_et = pd.read_csv(
        os.path.join('data', 'all_trials', 'cleaned', 'data_et.csv'))
    data_trial = pd.read_csv(
        os.path.join('data', 'all_trials', 'cleaned', 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join('data', 'all_trials', 'cleaned', 'data_subject.csv'))
    print('Imported from data/all_trials/cleaned: ')
    summarize_datasets(data_et, data_trial, data_subject)

    data_trial = init_choice_data_trial(data_trial)
    data_et = init_choice_data_et(data_et, data_trial)

    print('Data saved to ' +
          os.path.join('data', 'choice_task', 'raw') +
          ':')

    makedir('data', 'choice_task', 'raw')
    data_et.to_csv(
        os.path.join('data', 'choice_task', 'raw', 'data_et.csv'),
        index=False, header=True)
    data_trial.to_csv(
        os.path.join('data', 'choice_task', 'raw', 'data_trial.csv'),
        index=False, header=True)
    data_subject.to_csv(
        os.path.join('data', 'choice_task', 'raw', 'data_subject.csv'),
        index=False, header=True)
    summarize_datasets(data_et, data_trial, data_subject)


def clean_choice_data(use_adjusted_et_data=False):
    print('################################### \n'
          'Clean choice data \n'
          '################################### \n')

    if use_adjusted_et_data:
        print('Using adjusted data_et from' +
              os.path.join('data', 'choice_task', 'adjusted') + '\n')
        data_et = pd.read_csv(
            os.path.join('data', 'choice_task', 'adjusted', 'data_et.csv'))
        data_trial = pd.read_csv(
            os.path.join(
                'data', 'choice_task', 'adjusted', 'data_trial.csv'))
        data_subject = pd.read_csv(
            os.path.join(
                'data', 'choice_task', 'adjusted', 'data_subject.csv'))
    else:
        data_et = pd.read_csv(
            os.path.join('data', 'choice_task', 'uncorrected', 'data_et.csv'))
        data_trial = pd.read_csv(
            os.path.join(
                'data', 'choice_task', 'uncorrected', 'data_trial.csv'))
        data_subject = pd.read_csv(
            os.path.join(
                'data', 'choice_task', 'uncorrected', 'data_subject.csv'))

    print('Imported data from ' +
          os.path.join('data', 'choice_task', 'raw') + ':')
    if use_adjusted_et_data:
        print('and ' + os.path.join('data', 'choice_task', 'adjusted'))

    summarize_datasets(data_et, data_trial, data_subject)
    # Screening
    show_slow_reaction_times(data_trial)
    invalid_runs = invalid_choice_runs(data_trial, data_et, data_subject)

    # Remove invalid runs
    data_subject = clean_runs(data_subject, invalid_runs, 'data_subject')
    data_trial = clean_runs(data_trial, invalid_runs, 'data_trial')
    data_et = clean_runs(data_et, invalid_runs, 'data_et')

    # Remove Long trials
    data_trial = remove_long_trials(data_trial, 10000, 'data_trial')

    data_et = merge_by_index(data_et, data_trial, 'trial_duration_exact')
    data_et = remove_long_trials(data_et, 10000, 'data_et')
    data_et = data_et.drop(columns='trial_duration_exact')

    if use_adjusted_et_data:
        print('Data saved to ' +
              os.path.join('data', 'choice_task', 'adjusted', 'cleaned') +
              ':')

        makedir('data', 'choice_task', 'adjusted')

        data_et.to_csv(
            os.path.join('data', 'choice_task', 'adjusted', 'data_et.csv'),
            index=False, header=True)
        data_trial.to_csv(
            os.path.join('data', 'choice_task', 'adjusted', 'data_trial.csv'),
            index=False, header=True)
        data_subject.to_csv(
            os.path.join('data', 'choice_task', 'adjusted', 'data_subject.csv'),
            index=False, header=True)

    else:
        print('Data saved to ' +
              os.path.join('data', 'choice_task', 'uncorrected') +
              ':')

        makedir('data', 'choice_task', 'uncorrected')

        data_et.to_csv(
            os.path.join('data', 'choice_task', 'uncorrected', 'data_et.csv'),
            index=False, header=True)
        data_trial.to_csv(
            os.path.join('data', 'choice_task', 'uncorrected', 'data_trial.csv'),
            index=False, header=True)
        data_subject.to_csv(
            os.path.join('data', 'choice_task', 'uncorrected', 'data_subject.csv'),
            index=False, header=True)
    summarize_datasets(data_et, data_trial, data_subject)

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

    print(
        f"""Average reaction time below 10 seconds: \n"""
        f"""M = {round(m_below_10, 2)}, """
        f"""SD = {round(sd_below_10, 2)} \n"""
    )


def invalid_choice_runs(data_trial, data_et, data_subject):
    data_subject['residence'] = data_subject['Current Country of Residence']
    runs_not_us = data_subject.loc[
        data_subject['residence'] != 'United States', 'run_id']

    runs_low_fps = filter_runs_low_fps(data_trial, data_et, 10)
    # Run 144 was found to barely have any variation in
    # gaze transitions
    runs_additional_flaws = np.array([144])

    runs_biasedChoices = data_subject.loc[
        (data_subject['choseLL'] > 0.98) |
        (data_subject['choseLL'] < 0.02) |
        (data_subject['choseTop'] > 0.98) |
        (data_subject['choseTop'] < 0.02),
        'run_id']

    runs_missingLogK = data_subject.loc[
        pd.isna(data_subject['logK']), 'run_id']

    max_noise = 40
    runs_noisy_logK = data_subject.loc[
        data_subject['noise'] > max_noise, 'run_id']
    print(f'runs_noisy_logK means noise > {max_noise}')

    runs_pos_logK = data_subject.loc[
        data_subject['logK'] > 0, 'run_id']


    invalid_runs = list(
        set(runs_low_fps) |
        set(runs_additional_flaws) |
        set(runs_not_us) |
        set(runs_biasedChoices) |
        set(runs_missingLogK) |
        set(runs_noisy_logK) |
        set(runs_pos_logK))

    n_runs = len(data_trial['run_id'].unique())

    summary_output = pd.DataFrame(
        {
            'name': [
                'subjects_lowFPS',
                'additional_flaws',
                'runs_not_us',
                'runs_biasedChoices',
                'runs_missingLogK',
                'runs_noisy_logK',
                'runs_pos_logK',
                'total',
            ],
            'length': [
                len(runs_low_fps),
                len(runs_additional_flaws),
                len(runs_not_us),
                len(runs_biasedChoices),
                len(runs_missingLogK),
                len(runs_noisy_logK),
                len(runs_pos_logK),
                len(invalid_runs)
            ],
            'percent': [
                len(runs_low_fps) / n_runs,
                len(runs_additional_flaws) / n_runs,
                len(runs_not_us) / n_runs,
                len(runs_biasedChoices) / n_runs,
                len(runs_missingLogK) / n_runs,
                len(runs_noisy_logK) / n_runs,
                len(runs_pos_logK) / n_runs,
                len(invalid_runs) / n_runs
            ]
        }
    )

    print(
        f"""\n"""
        f"""n={n_runs} runs in total. Invalid runs for choice task: \n"""
        f"""{round(summary_output, 2)} \n""")

    return invalid_runs


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
        f"""is coming from: \n"""
        f"""{grouped_missing_et} \n"""
    )


def remove_long_trials(data_raw, max_duration, name):
    data = data_raw.loc[data_raw['trial_duration_exact'] < max_duration, :]

    print(
        f"""Removing long trials (>10s) from {name}: \n"""
        f"""   Raw: {len(data_raw)} \n"""
        f"""   Cleaned: {len(data)} \n""")

    return data
