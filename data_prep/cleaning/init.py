import os

import pandas as pd

from data_prep.cleaning.drop_na_eye_tracking import drop_na_data_et
from data_prep.cleaning.filter_approved import runs_not_approved
from data_prep.cleaning.invalid_runs import filter_invalid_runs, clean_runs
from data_prep.cleaning.prolific_ids import match_ids_with_subjects, drop_duplicate_ids
from data_prep.cleaning.replace_subject_vars import replace_subject_variables
from utils.path import makedir
from utils.tables import summarize_datasets


def global_cleaning():

    print('################################### \n'
          'Clean global datasets \n'
          '################################### \n')

    data_et = pd.read_csv(
        os.path.join('data', 'all_trials', 'added_var', 'data_et.csv'))
    data_trial = pd.read_csv(
        os.path.join('data', 'all_trials', 'added_var', 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join('data', 'all_trials', 'added_var', 'data_subject.csv'))
    print('Imported from data/all_trials/added_var:')
    summarize_datasets(data_et, data_trial, data_subject)

    print(len(data_subject.loc[data_subject['status'] == 'APPROVED',
        'prolificID'].unique()))

    data_et = drop_na_data_et(data_et)
    data_subject = replace_subject_variables(data_subject)

    # Filter Prolific data
    runs_not_prolific = data_subject.loc[
        data_subject['status'] == 'NOTPROLIFIC', 'run_id']

    print(
        f""" \n"""
        f"""Filtering Prolific Data: \n"""
        f"""n={len(runs_not_prolific)} were not from Prolific """
        f"""(e.g. from task development instead) and will be removed: \n""")

    data_et = clean_runs(data_et, runs_not_prolific, 'data_et')
    data_trial = clean_runs(data_trial, runs_not_prolific, 'data_trial')
    data_subject = clean_runs(data_subject, runs_not_prolific, 'data_subject')

    runs_without_prolific_id = data_subject.loc[
        pd.isna(data_subject['prolificID']), 'run_id']

    runs_with_prolific_ids = data_subject.loc[
        pd.notna(data_subject['prolificID']), 'run_id']

    print(f"""n={len(runs_without_prolific_id)} """
          f"""subjects have no prolific IDs. \n"""
          f"""n={len(runs_with_prolific_ids)} runs have Prolific IDs. """)

    if len(runs_without_prolific_id) > 0:
        data_et = clean_runs(data_et, runs_without_prolific_id,
                             'data_et')
        data_trial = clean_runs(data_trial, runs_without_prolific_id,
                                'data_trial')
        data_subject = clean_runs(data_subject, runs_without_prolific_id,
                                  'data_subject')

    # Clean multi-attempts
    print('Clean for multiple attempts: ')
    data_subject = drop_duplicate_ids(data_subject)

    print(data_subject.loc[data_subject['status']=='APPROVED', :])

    data_trial = match_ids_with_subjects(
        data_trial, data_subject, 'data_trial')
    data_et = match_ids_with_subjects(
        data_et, data_subject, 'data_et')

    # Filter approved
    print(f"""\nFilter approved runs: """)
    unapproved_runs = runs_not_approved(data_subject)
    data_et = clean_runs(data_et, unapproved_runs, 'data_et')
    data_trial = clean_runs(data_trial, unapproved_runs, 'data_trial')
    data_subject = clean_runs(data_subject, unapproved_runs, 'data_subject')

    excluded_runs = filter_invalid_runs(
        data_trial, data_et, data_subject)

    data_et = clean_runs(data_et, excluded_runs, 'data_et')
    data_trial = clean_runs(data_trial, excluded_runs, 'data_trial')
    data_subject = clean_runs(data_subject, excluded_runs, 'data_subject')


    makedir('data', 'all_trials', 'cleaned')
    print(f"""Writing datasets to """
          f"""{os.path.join('data', 'all_trials', 'cleaned')}""")

    data_et.to_csv(
        os.path.join('data', 'all_trials', 'cleaned',
                     'data_et.csv'),
        index=False, header=True)
    data_trial.to_csv(
        os.path.join('data', 'all_trials', 'cleaned',
                     'data_trial.csv'),
        index=False, header=True)
    data_subject.to_csv(
        os.path.join('data', 'all_trials', 'cleaned',
                     'data_subject.csv'),
        index=False, header=True)



    summarize_datasets(data_et, data_trial, data_subject)
