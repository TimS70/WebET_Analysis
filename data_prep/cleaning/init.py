import os

import pandas as pd

from data_prep.cleaning.drop_na_eye_tracking import drop_na_data_et
from data_prep.cleaning.filter_approved import filter_approved_runs
from data_prep.cleaning.find_invalid_runs.invalid_runs import invalid_runs_global, clean_runs
from data_prep.cleaning.prolific_ids import drop_duplicate_ids
from data_prep.cleaning.replace_subject_vars import replace_subject_variables
from utils.tables import summarize_datasets, save_all_three_datasets, \
    load_all_three_datasets


def global_cleaning():

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
        data_trial, data_et, data_subject)

    data_et = clean_runs(data_et, excluded_runs, 'data_et')
    data_trial = clean_runs(data_trial, excluded_runs, 'data_trial')
    data_subject = clean_runs(data_subject, excluded_runs, 'data_subject')

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'all_trials', 'cleaned'))


# noinspection DuplicatedCode
def match_runs(data_subject, data_trial, data_et):
    # match data_trial
    runs_subject_but_not_trial = data_subject.loc[
        ~data_subject['run_id'].isin(data_trial['run_id']),
        'run_id'].unique()

    print(
        f"""n={len(runs_subject_but_not_trial)} approved runs """
        f"""had no data on cognition_run.""")

    data_subject = data_subject.loc[
                   data_subject['run_id'].isin(data_trial['run_id']), :]

    # Match data_et
    runs_subject_but_not_et = data_subject.loc[
        ~data_subject['run_id'].isin(data_et['run_id']),
        'run_id'].unique()

    print(
        f"""n={len(runs_subject_but_not_et)} approved runs """
        f"""had no eye-tracking data on cognition_run. \n""")

    data_subject = data_subject.loc[
        data_subject['run_id'].isin(data_et['run_id']), :]

    data_trial = data_trial.loc[
                 data_trial['run_id'].isin(data_subject['run_id']), :]
    data_et = data_et.loc[
                 data_et['run_id'].isin(data_subject['run_id']), :]

    summarize_datasets(data_et, data_trial, data_subject)

    return data_subject, data_trial, data_et
