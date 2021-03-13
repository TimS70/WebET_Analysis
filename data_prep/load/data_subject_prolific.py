import os

import numpy as np
import pandas as pd

from data_prep.load.survey_data import create_survey_data
from utils.path import makedir


def create_data_subject(data_raw):
    data_subject = data_raw.loc[
                   :,
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
    data_prolific_int = pd.read_csv(
        os.path.join('data', 'prolific', 'prolific_export_int.csv')) \
        .rename(columns={'participant_id': 'prolificID'})

    data_prolific_us = pd.read_csv(
        os.path.join('data', 'prolific', 'prolific_export_us.csv')) \
        .rename(columns={'participant_id': 'prolificID'})

    data_prolific = data_prolific_int \
        .append(data_prolific_us)
    return data_prolific


def add_data_from_prolific(data_subject):
    data_prolific = read_prolific_data()

    data_subject = data_subject.merge(
        data_prolific, on='prolificID', how='left')
    data_subject['status'] = data_subject['status'].fillna('NOTPROLIFIC')
    data_subject.loc[:, ['run_id', 'prolificID']].head(5)

    return data_subject
