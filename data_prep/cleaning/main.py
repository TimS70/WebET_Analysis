import os

import numpy as np
import pandas as pd

from analysis.compare_datasets import check_unequal_trial_numbers
from data_prep.cleaning.drop_invalid_data.runs import clean_runs, \
    filter_approved_runs, match_runs
from data_prep.cleaning.drop_invalid_data.et_data import drop_na_data_et
from data_prep.cleaning.drop_invalid_data.prolific_ids import drop_duplicate_ids
from data_prep.cleaning.drop_invalid_data.trials import clean_trial_duration
from data_prep.cleaning.find_invalid_runs.both_tasks import filter_runs_low_fps
from data_prep.cleaning.find_invalid_runs.choice import filter_bad_log_k, \
    filter_runs_not_us, filter_runs_precision, filter_runs_offset, \
    filter_hit_ratio
from data_prep.cleaning.find_invalid_runs.main import invalid_runs_global
from data_prep.cleaning.fix_task import show_empty_fix_trials, \
    show_trials_high_t_task
from data_prep.cleaning.replace import replace_subject_variables
from utils.combine_frames import merge_by_index
from utils.save_data import summarize_datasets, save_all_three_datasets, \
    load_all_three_datasets


def clean_global_data(max_t_task=5500, min_fps=3):
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


def combine_runs(all_runs, *args):
    for runs in [*args]:
        all_runs = list(
            set(all_runs) |
            set(runs))

    return all_runs


def clean_data_choice(
        us_sample,
        min_hit_ratio, max_precision,
        max_offset, min_fps, min_rt, max_rt,
        min_choice_percentage, max_choice_percentage,
        exclude_runs=None, filter_log_k=True):
    print('################################### \n'
          'Clean choice data \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'choice_task', 'added_var'))

    # Screening
    invalid_runs = []
    n_runs = len(data_trial['run_id'].unique())
    summary = []

    if us_sample:
        runs_not_us = filter_runs_not_us(data_subject)
        invalid_runs = combine_runs(invalid_runs, runs_not_us)
        summary.append(['runs_no_variance',
                        len(runs_not_us),
                        len(runs_not_us) / n_runs])

    if min_fps is not None:
        runs_low_fps = filter_runs_low_fps(
            data_trial, data_et, min_fps=min_fps)
        invalid_runs = combine_runs(invalid_runs, runs_low_fps)
        summary.append(['runs_low_fps',
                        len(runs_low_fps),
                        len(runs_low_fps) / n_runs])

    if max_precision is not None:
        runs_low_precision = filter_runs_precision(
            data_subject, max_precision=max_precision)
        invalid_runs = combine_runs(
            invalid_runs, runs_low_precision)
        summary.append(['runs_low_precision',
                        len(runs_low_precision),
                        len(runs_low_precision) / n_runs])

    if max_offset is not None:
        runs_high_offset = filter_runs_offset(
            data_subject, max_offset=max_offset)
        invalid_runs = combine_runs(invalid_runs, runs_high_offset)
        summary.append(['runs_high_offset',
                        len(runs_high_offset),
                        len(runs_high_offset) / n_runs])

    if min_hit_ratio is not None:
        runs_low_hit_ratio = filter_hit_ratio(
            data_subject, min_hit_ratio=min_hit_ratio)
        invalid_runs = combine_runs(invalid_runs, runs_low_hit_ratio)
        summary.append(['runs_low_hit_ratio',
                        len(runs_low_hit_ratio),
                        len(runs_low_hit_ratio) / n_runs])

    # These runs have barely have any variation in gaze points
    if exclude_runs is not None:
        runs_no_variance = np.intersect1d(
            data_subject['run_id'].unique(), exclude_runs)
        invalid_runs = combine_runs(invalid_runs, runs_no_variance)
        summary.append(['runs_no_variance',
                        len(runs_no_variance),
                        len(runs_no_variance) / n_runs])

    if min_choice_percentage is not None:
        runs_biased_ss = data_subject.loc[
            data_subject['choseLL'] < min_choice_percentage, 'run_id']
        invalid_runs = combine_runs(invalid_runs, runs_biased_ss)
        summary.append(['runs_biased_SS',
                        len(runs_biased_ss),
                        len(runs_biased_ss) / n_runs])

    if max_choice_percentage is not None:
        runs_biased_ll = data_subject.loc[
            data_subject['choseLL'] > max_choice_percentage, 'run_id']
        invalid_runs = combine_runs(invalid_runs, runs_biased_ll)
        summary.append(['runs_biased_LL',
                        len(runs_biased_ll),
                        len(runs_biased_ll) / n_runs])

    if filter_log_k:
        runs_missing_log_k, runs_noisy_log_k, runs_pos_log_k = \
            filter_bad_log_k(data_subject, max_noise=40)
        invalid_runs = combine_runs(
            invalid_runs,
            runs_missing_log_k, runs_noisy_log_k,
            runs_pos_log_k)
        summary.append([
            [
                'runs_missing_log_k',
                len(runs_missing_log_k),
                len(runs_missing_log_k) / n_runs],
            [
                'runs_noisy_log_k',
                len(runs_noisy_log_k),
                len(runs_noisy_log_k) / n_runs],
            [
                'runs_pos_log_k',
                len(runs_pos_log_k),
                len(runs_pos_log_k) / n_runs]])

    summary.append(['total',
                    len(invalid_runs),
                    len(invalid_runs) / n_runs])

    summary = pd.DataFrame(
        summary,
        columns=['name', 'length', 'percent'])

    print(f"""In total, n={len(invalid_runs)} have to be """
          f"""removed from n={n_runs} runs: \n"""
          f"""{summary}""")

    # Remove invalid runs
    data_subject = clean_runs(data_subject, invalid_runs, 'data_subject')
    data_trial = clean_runs(data_trial, invalid_runs, 'data_trial')
    data_et = clean_runs(data_et, invalid_runs, 'data_et')

    if (min_rt is not None) & (max_rt is not None):
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
