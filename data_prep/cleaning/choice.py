import os

import numpy as np
import pandas as pd

from data_prep.choice import add_log_k
from data_prep.cleaning.invalid_runs \
    import filter_runs_low_fps, clean_runs
from utils.data_frames import merge_by_index
from utils.path import makedir
from utils.tables import summarize_datasets, load_all_three_datasets, save_all_three_datasets, write_csv


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

    print(
        f"""Average reaction time below 10 seconds: \n"""
        f"""M = {round(m_below_10, 2)}, """
        f"""SD = {round(sd_below_10, 2)} \n"""
    )


def invalid_choice_runs(data_trial, data_et, data_subject):
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

    write_csv(grouped_us, 'us_vs_international_sample.csv',
              'results', 'tables', 'demographics')

    print(
        f"""{len(runs_not_us)} runs do not reside inside the us. """
        f"""However, since their behavior does not differ much, """
        f"""we will keep them for now. \n \n"""
        f"""grouped_us.transpose: \n"""
        f"""{grouped_us} \n""")

    runs_low_fps = filter_runs_low_fps(data_trial, data_et, 5)

    max_precision = 0.15
    runs_low_precision = data_subject.loc[
        data_subject['precision'] > max_precision, 'run_id']
    print(f"""Maximum precision means >{max_precision}. \n""")

    max_offset = 0.5
    runs_high_offset = data_subject.loc[
        data_subject['offset'] > max_offset, 'run_id']
    print(f"""Maximum offset means >{max_offset}. \n""")

    runs_bad_quality = list(
        set(runs_low_fps) |
        set(runs_low_precision) |
        set(runs_high_offset))

    print(
        f"""In total, {len(runs_bad_quality)} runs were excluded """
        f"""because of bad data quality. \n""")

    # Run 144 was found to barely have any variation in
    # gaze transitions
    runs_additional_flaws = np.array([144])

    runs_biasedChoices = data_subject.loc[
        (data_subject['choseLL'] > 0.99) |
        (data_subject['choseLL'] < 0.01),
        'run_id']

    grouped_trials_biased = data_trial.loc[
        data_trial['run_id'].isin(runs_biasedChoices), :] \
        .groupby(
            ['run_id', 'choseLL'],
            as_index=False).agg(
            n=('trial_index', 'count'))
    grouped_trials_biased = grouped_trials_biased \
        .loc[grouped_trials_biased['n'] > 1, :]

    print(
        f"""grouped_trials_biased \n"""
        f"""{grouped_trials_biased} \n"""
    )

    runs_missingLogK = data_subject.loc[
        pd.isna(data_subject['logK']), 'run_id']

    max_noise = 40
    runs_noisy_logK = data_subject.loc[
        pd.notna(data_subject['logK']) &
        (data_subject['noise'] > max_noise), 'run_id']
    print(
        f"""runs_noisy_logK means noise > {max_noise}. \n""")

    # runs_pos_logK = data_subject.loc[
    #     data_subject['logK'] > 0, 'run_id']

    invalid_runs = list(

        set(runs_additional_flaws) |
        set(runs_biasedChoices) |
        set(runs_missingLogK) |
        set(runs_noisy_logK) |
        # set(runs_pos_logK) |
        set(runs_low_fps) |
        set(runs_low_precision) |
        set(runs_high_offset))

    n_runs = len(data_trial['run_id'].unique())

    summary_output = pd.DataFrame(
        {
            'name': [
                'run nr. 144',
                'runs_biasedChoices',
                'runs_missingLogK',
                'runs_noisy_logK',
                # 'runs_pos_logK',
                'subjects_lowFPS',
                'runs_low_precision',
                'runs_high_offset',
                'total',
            ],
            'length': [
                len(runs_additional_flaws),
                len(runs_biasedChoices),
                len(runs_missingLogK),
                len(runs_noisy_logK),
                # len(runs_pos_logK),
                len(runs_low_fps),
                len(runs_low_precision),
                len(runs_high_offset),
                len(invalid_runs)
            ],
            'percent': [
                len(runs_additional_flaws) / n_runs,
                len(runs_biasedChoices) / n_runs,
                len(runs_missingLogK) / n_runs,
                len(runs_noisy_logK) / n_runs,
                # len(runs_pos_logK) / n_runs,
                len(runs_low_fps) / n_runs,
                len(runs_low_precision) / n_runs,
                len(runs_high_offset) / n_runs,
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

    if len(grouped_missing_et) > 0:
        print(
            f"""{len(grouped_missing_et)} runs have at least one """
            f"""empty (et-related) trial. \n"""
            f"""That is where the difference of """
            f"""{grouped_missing_et['trial_index'].sum()} trials """
            f"""is coming from: \n"""
            f"""{grouped_missing_et} \n"""
        )
    else:
        print('No difference in trial number found')


def remove_long_trials(data_raw, max_duration, name):
    data = data_raw.loc[data_raw['trial_duration_exact'] < max_duration, :]

    print(
        f"""Removing long trials (>{max_duration}) from {name}: \n"""
        f"""   Raw: {len(data_raw)} \n"""
        f"""   Cleaned: {len(data)} \n""")

    return data
