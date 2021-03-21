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

    data_subject = add_and_filter_prolific(data_subject)

    makedir('data', 'all_trials', 'combined')
    data_subject.to_csv(
        os.path.join('data', 'all_trials', 'combined', 'data_subject.csv'),
        index=False, header=True)
    print('data_subject saved!')

    return data_subject


def create_data_prolific(data_subject):
    data_prolific = read_prolific_data()

    data_subject = data_subject.rename(columns={
        'chosenAmount': 'bonus_USD',
        'chosenDelay': 'bonus_delay'
    })

    data_prolific = data_prolific.merge(
        data_subject.loc[:, np.append(
                ['prolificID'],
                data_subject.columns.difference(data_prolific.columns))],
        on='prolificID',
        how='left')

    makedir('data', 'all_trials', 'combined')
    data_prolific.to_csv(
        os.path.join('data', 'all_trials', 'combined', 'data_prolific.csv'),
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


def add_and_filter_prolific(data_subject):

    print(
        f"""Runs without prolific ID: """
        f"""{sum(pd.isna(data_subject['prolificID']))}""")

    data_prolific = read_prolific_data()

    id_prolific = data_prolific['prolificID'].unique()
    id_cognition = data_subject.loc[
        pd.notna(data_subject['prolificID']), 'prolificID'].unique()

    id_prolific_but_not_cognition = np.setdiff1d(
        id_prolific, id_cognition, assume_unique=True)

    print(
        f"""n={len(id_prolific_but_not_cognition)} prolific IDs """
        f"""are in Prolific not in cognition.run: \n"""
        f"""{id_prolific_but_not_cognition} \n""")

    id_cognition_but_not_prolific = np.setdiff1d(
        id_cognition, id_prolific, assume_unique=True)

    print(
        f"""n={len(id_cognition_but_not_prolific)} prolific IDs """
        f"""are in cognition.run but not in Prolific: \n"""
        f"""{id_cognition_but_not_prolific} \n""")

    print(
        f"""ID '5c670a430d80fd00014264f9' was asked via Prolific """
        f"""but have not responded yet.""")

    data_subject = data_subject.merge(
        data_prolific, on='prolificID', how='left')

    data_subject = data_subject.append(
        data_prolific.loc[
            data_prolific['prolificID'].isin(
                id_prolific_but_not_cognition),
            :])

    ids_approved = data_subject.loc[
        data_subject['status'] == 'APPROVED', 'prolificID'].unique()

    print(
        f"""Unique approved IDs: {len(ids_approved)} \n"""
        f"""ID '5c670a430d80fd00014264f9' was asked via Prolific """
        f"""but have not responded yet.""")

    summary_na = data_subject.loc[
        pd.isna(data_subject['status']),
        ['run_id', 'prolificID', 'session_id', 'status']
    ]

    print(f"""Runs with missing status: \n {summary_na}""")

    return data_subject
