import os

import numpy as np
import pandas as pd

from data_prep.load.survey_data import create_survey_data
from utils.path import makedir
from utils.save_data import write_csv


def create_data_prolific(data_subject, path_origin):
    data_prolific = read_prolific_data(path_origin=path_origin)

    data_subject = data_subject.rename(columns={
        'chosenAmount': 'bonus_USD',
        'chosenDelay': 'bonus_delay'})

    data_prolific = data_prolific.merge(
        data_subject.loc[:, np.append(
                ['prolificID'],
                data_subject.columns.difference(data_prolific.columns))],
        on='prolificID',
        how='left')

    return data_prolific


def read_prolific_data(path_origin):

    data_prolific_free = pd.read_csv(
        os.path.join(path_origin, 'prolific_export_free.csv')) \
        .rename(columns={'participant_id': 'prolificID'})

    data_prolific_int = pd.read_csv(
        os.path.join(path_origin, 'prolific_export_int.csv')) \
        .rename(columns={'participant_id': 'prolificID'})

    data_prolific_us = pd.read_csv(
        os.path.join(path_origin, 'prolific_export_us.csv')) \
        .rename(columns={'participant_id': 'prolificID'})

    data_prolific = data_prolific_int \
        .append(data_prolific_us) \
        .append(data_prolific_free)

    return data_prolific


def integrate_prolific_data(file_origin, path_prolific, path_target):
    data_subject = pd.read_csv(file_origin)

    print(f"""n={sum(pd.isna(data_subject['prolificID']))} """
          f"""runs without Prolific ID """)

    data_prolific = read_prolific_data(path_origin=path_prolific)

    id_prolific = data_prolific['prolificID'].unique()
    id_cognition = data_subject.loc[
        pd.notna(data_subject['prolificID']), 'prolificID'].unique()

    id_prolific_but_not_cognition = np.setdiff1d(
        id_prolific, id_cognition, assume_unique=True)

    print(f"""n={len(id_prolific_but_not_cognition)} prolific IDs """
          f"""are in Prolific but not in cognition.run: \n"""
          f"""{id_prolific_but_not_cognition} \n""")

    id_cognition_but_not_prolific = np.setdiff1d(
        id_cognition, id_prolific, assume_unique=True)

    print(f"""n={len(id_cognition_but_not_prolific)} prolific IDs """
          f"""are in cognition.run but not in Prolific: \n"""
          f"""{id_cognition_but_not_prolific} \n""")

    print(f"""ID '5c670a430d80fd00014264f9' was asked via Prolific """
          f"""but have not responded yet.""")

    data_subject = data_subject.merge(
        data_prolific, on='prolificID', how='left')

    data_subject = data_subject.append(data_prolific[
            data_prolific['prolificID'].isin(id_prolific_but_not_cognition)])

    ids_approved = data_subject.loc[
        data_subject['status'] == 'APPROVED', 'prolificID'].unique()

    print(f"""Unique approved IDs: {len(ids_approved)} \n"""
          f"""ID '5c670a430d80fd00014264f9' was asked via Prolific """
          f"""but have not responded yet.""")

    summary_na = data_subject.loc[
        pd.isna(data_subject['status']),
        ['run_id', 'prolificID', 'session_id', 'status']]

    print(f"""Runs with missing status: \n {summary_na}""")

    write_csv(data=data_subject, file_name='data_subject.csv',
              path=path_target)

    data_prolific = create_data_prolific(data_subject, path_prolific)
    write_csv(data=data_prolific, file_name='data_prolific.csv',
              path=path_target)
