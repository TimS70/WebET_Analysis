import os

import numpy as np
import pandas as pd

from data_prep.load.survey_data import create_survey_data
from utils.path import makedir


def create_data_subject(data_raw):
    data_subject = data_raw.loc[:,
        [
           'run_id', 'chinFirst', 'choiceTask_amountLeftFirst',
           'browser', 'browser_version', 'device',
           'platform', 'platform_version', 'user_agent',
           'chosenAmount', 'chosenDelay',
           'webcam_label', 'webcam_fps', 'webcam_height', 'webcam_width'
        ]
        ].drop_duplicates()

    survey_data = create_survey_data(data_raw)

    data_subject = data_subject \
        .merge(
            survey_data,
            on='run_id',
            how='left') \
        .rename(columns={'age': 'birthyear'})

    data_subject = add_data_from_prolific(data_subject)

    makedir('data', 'all_trials', 'combined')
    data_subject.to_csv(
        os.path.join('data', 'all_trials', 'combined', 'data_subject.csv'),
        index=False, header=True)
    print('data_subject saved!')

    return data_subject


def create_data_prolific(data_subject):
    data_prolific = read_prolific_data()

    temp = data_subject.rename(columns={
        'chosenAmount': 'bonus_USD',
        'chosenDelay': 'bonus_delay'
    }
    )

    data_prolific = data_prolific.merge(
        temp.loc[:, np.append(
                ['prolificID'],
                temp.columns.difference(data_prolific.columns))],
        on='prolificID',
        how='left')

    makedir('data', 'prolific')
    data_prolific.to_csv(
        os.path.join('data', 'prolific', 'data_prolific.csv'),
                     index=False, header=True)

    print('data_prolific saved!')


def read_prolific_data():

    data_prolific_free = pd.read_csv(
        os.path.join('data', 'prolific', 'prolific_export_free.csv')) \
        .rename(columns={'participant_id': 'prolificID'})

    data_prolific_int = pd.read_csv(
        os.path.join('data', 'prolific', 'prolific_export_int.csv')) \
        .rename(columns={'participant_id': 'prolificID'})

    data_prolific_us = pd.read_csv(
        os.path.join('data', 'prolific', 'prolific_export_us.csv')) \
        .rename(columns={'participant_id': 'prolificID'})

    data_prolific = data_prolific_int \
        .append(data_prolific_us) \
        .append(data_prolific_free)

    return data_prolific


def add_data_from_prolific(data_subject):
    data_prolific = read_prolific_data()

    data_subject = data_subject.merge(
        data_prolific, on='prolificID', how='left')

    data_subject.loc[
        pd.isna(data_subject['prolificID']) |
        (data_subject['prolificID'] == 'Tim'),
        'status'] = 'NOTPROLIFIC'

    summary_na = data_subject.loc[
        pd.isna(data_subject['status']),
        ['run_id', 'prolificID', 'session_id', 'status']
    ]

    prolific_approved = data_prolific.loc[
        data_prolific['status'] == 'APPROVED',
        'prolificID'].unique()

    cognition_approved = data_subject.loc[
        data_subject['status'] == 'APPROVED',
        'prolificID'].unique()

    lonely_prolific_runs = np.setdiff1d(
        prolific_approved, cognition_approved)

    print(
        f"""n={len(summary_na)} runs could not be found in """
        f"""Prolific for being approved. \n"""
        f"""{summary_na} \n\n"""
        f"""prolific_approved: n={len(prolific_approved)} \n"""
        f"""cognition_approved: n={len(cognition_approved)} \n\n"""
        f"""n={len(lonely_prolific_runs)} runs were on """
        f"""Prolific but did have any data: """
        f"""{lonely_prolific_runs}""")


    return data_subject
