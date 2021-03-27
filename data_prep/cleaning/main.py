import os

import pandas as pd

from analysis.compare_datasets import check_unequal_trial_numbers
from data_prep.cleaning.drop_invalid_data.runs import clean_runs, filter_approved_runs, match_runs
from data_prep.cleaning.drop_invalid_data.et_data import drop_na_data_et
from data_prep.cleaning.drop_invalid_data.prolific_ids import drop_duplicate_ids
from data_prep.cleaning.drop_invalid_data.trials import clean_trial_duration
from data_prep.cleaning.find_invalid_runs.main import invalid_runs_global, invalid_runs_fix, invalid_runs_choice
from data_prep.cleaning.fix_task import show_empty_fix_trials, show_trials_high_t_task
from data_prep.cleaning.replace import replace_subject_variables
from utils.combine_frames import merge_by_index
from utils.save_data import summarize_datasets, save_all_three_datasets, \
    load_all_three_datasets


def clean_global_data():

    print('################################### \n'
          'Clean global datasets \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'all_trials', 'added_var'))

    data_et = drop_na_data_et(data_et)
    data_subject = replace_subject_variables(data_subject)

    # Filter Prolific data
    runs_not_prolific = data_subject.loc[
        pd.isna(data_subject['prolificID']), 'run_id']

    print(
        f""" \n"""
        f"""Filtering Prolific Data: \n"""
        f"""n={len(runs_not_prolific)} runs do not have a Prolific ID """
        f"""(e.g. from task development instead) and will be removed: \n""")

    data_et = clean_runs(data_et, runs_not_prolific, 'data_et')
    data_trial = clean_runs(data_trial, runs_not_prolific, 'data_trial')
    data_subject = clean_runs(data_subject, runs_not_prolific, 'data_subject')

    runs_without_prolific_id = data_subject.loc[
        pd.isna(data_subject['prolificID']), 'run_id']

    if len(runs_without_prolific_id) > 0:
        data_et = clean_runs(data_et, runs_without_prolific_id,
                             'data_et')
        data_trial = clean_runs(data_trial, runs_without_prolific_id,
                                'data_trial')
        data_subject = clean_runs(data_subject, runs_without_prolific_id,
                                  'data_subject')

    data_subject, data_trial, data_et = filter_approved_runs(
        data_subject, data_trial, data_et)

    # Clean multi-attempts
    print('Clean for multiple attempts: ')
    data_subject = drop_duplicate_ids(data_subject)
    data_trial = data_trial.loc[data_trial['run_id'].isin(
        data_subject['run_id']), :]
    data_et = data_et.loc[data_et['run_id'].isin(
        data_subject['run_id']), :]
    summarize_datasets(data_et, data_trial, data_subject)

    print('Match runs: ')
    data_subject, data_trial, data_et = match_runs(
        data_subject, data_trial, data_et)

    # Other invalid participants
    excluded_runs = invalid_runs_global(
        data_trial, data_et, data_subject,
        max_t_task=max_t_task,
        min_fps=min_fps)

    data_et = clean_runs(data_et, excluded_runs, 'data_et')
    data_trial = clean_runs(data_trial, excluded_runs, 'data_trial')
    data_subject = clean_runs(data_subject, excluded_runs, 'data_subject')

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'all_trials', 'cleaned'))


def clean_data_fix(max_t_task=5500):
    print('################################### \n'
          'Clean fix task datasets \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'fix_task', 'raw'))

    # Screening
    show_empty_fix_trials(data_trial)
    show_trials_high_t_task(
        data_trial, max_t_task=max_t_task)

    data_trial = clean_trial_duration(
        data_trial, 0, max_t_task, 'data_trial')
    data_et = clean_trial_duration(
        data_et, 0, max_t_task, 'data_et')

    data_trial = data_trial[pd.notna(data_trial['x_count'])]

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'fix_task',
                                         'cleaned'))


def clean_data_choice(
        min_hit_ratio=0.8, max_precision=0.15,
        max_offset=0.5, min_fps=5,
        min_rt=400, max_rt=10000,
        min_choice_percentage=0.01,
        max_choice_percentage=0.99):

    print('################################### \n'
          'Clean choice data \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'choice_task', 'added_var'))

    print(data_subject.columns)
    # Screening
    invalid_runs = invalid_runs_choice(
        data_trial, data_et, data_subject,
        min_hit_ratio=min_hit_ratio,
        max_precision=max_precision,
        max_offset=max_offset,
        min_fps=min_fps,
        min_choice_percentage = min_choice_percentage,
        max_choice_percentage = max_choice_percentage)

    # Remove invalid runs
    data_subject = clean_runs(data_subject, invalid_runs, 'data_subject')
    data_trial = clean_runs(data_trial, invalid_runs, 'data_trial')
    data_et = clean_runs(data_et, invalid_runs, 'data_et')

    # Remove Long trials
    data_trial = clean_trial_duration(
        data_trial, min_rt, max_rt, 'data_trial')

    data_et = merge_by_index(
        data_et, data_trial, 'trial_duration_exact')
    data_et = clean_trial_duration(
        data_et, min_rt, max_rt, 'data_et')
    data_et = data_et.drop(columns='trial_duration_exact')

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'choice_task', 'cleaned'))

    check_unequal_trial_numbers(data_et, data_trial)
