import datetime

import matplotlib.pyplot as plt
import pandas as pd

from tqdm import tqdm

from utils.combine_data import merge_by_subject
from utils.path import makedir


def add_subject_variables(data_subject, data_trial):
    data_subject = add_fps_subject_level(data_subject, data_trial)
    data_subject = add_max_trials(data_subject, data_trial)
    data_subject = add_glasses_binary(data_subject)
    data_subject = add_recorded_date(data_subject, data_trial)
    data_subject = add_employment_status(data_subject)
    data_subject = add_full_time_binary(data_subject)

    return data_subject


def add_fps_subject_level(data_subject, data_trial):
    data_subject = merge_by_subject(data_subject, data_trial, 'fps')
    plt.hist(data_subject['fps'], bins=15)
    plt.savefig('plots/fps/chin_first_0.png')
    print('data_subject: Added fps: See plots/fps/ \n')

    return data_subject


def add_max_trials(data_subject, data_trial):
    data_subject = data_subject \
        .merge(
        data_trial.groupby(['run_id'], as_index=False)['trial_index'].max(),
        on=['run_id'],
        how='left') \
        .rename(columns={'trial_index': 'max_trial'})

    example = data_subject.loc[
        :, ['run_id', 'prolificID', 'max_trial']
    ].head(5)

    print(
        f"""data_subject: Added max_trial: \n """
        f"""{example} \n""")

    return data_subject


def add_glasses_binary(data_subject):
    data_subject['glasses_binary'] = data_subject['sight'] \
        .replace({'contactLenses': 0,
                  'glasses': 1,
                  'notCorrected': 0,
                  'perfectSight': 0}
                 )

    example = pd.crosstab(
        index=data_subject['glasses_binary'],
        columns="count")

    n_missing = len(data_subject.loc[
        pd.isna(data_subject['glasses_binary']), :])

    print(
        f"""data_subject: Added glasses_binary: \n"""
        f"""N Missing values: {n_missing} \n \n"""
        f"""{example} \n""")

    return data_subject


def add_recorded_date(data_subject, data_trial):
    output = []

    for subject in tqdm(
            data_trial['run_id'].unique(),
            desc='Add recorded date for each participant: '):
        this_subject = data_trial.loc[data_trial['run_id'] == subject] \
            .reset_index(drop=True)
        date_time_obj = datetime.datetime.strptime(
            this_subject.loc[0, 'recorded_at'], '%Y-%m-%d %H:%M:%S')

        output.append([this_subject.loc[0, 'run_id'], date_time_obj.date()])

    output = pd.DataFrame(output, columns=['run_id', 'recorded_date'])

    if 'recorded_date' in data_subject.columns:
        data_subject = data_subject.drop(columns=['recorded_date'])

    data_subject = data_subject.merge(output, on='run_id', how='left')

    example = data_subject.loc[
              :, ['run_id', 'prolificID', 'recorded_date']
              ].head(5)

    print(
        f"""data_subject: Added recorded_date: \n"""
        f"""{example} \n""")

    return data_subject


def add_employment_status(data_subject):
    data_subject['employment_status'] = data_subject['Employment Status'].replace({
        """Not in paid work (e.g. homemaker', 'retired or disabled)""": 'not_in_paid_work',
        'DATA EXPIRED': 'Other',
        'Unemployed (and job seeking)': 'not_in_paid_work',
        'Due to start a new job within the next month': 'Other'
    })

    example = pd.crosstab(
        index=data_subject['employment_status'],
        columns="count")

    print(
        f"""data_subject: Added employment_status: \n"""
        f"""{example} \n""")

    return data_subject


def add_full_time_binary(data_subject):
    data_subject['fullTime_binary'] = data_subject['Employment Status'].replace({
        'Other': 0,
        'Full-Time': 1,
        'Part-Time': 0,
        "Not in paid work (e.g. homemaker', 'retired or disabled)": 0,
        'Unemployed (and job seeking)': 0,
        'DATA EXPIRED': 0
    })

    example = pd.crosstab(
        index=data_subject['fullTime_binary'],
        columns="count")

    print(
        f"""data_subject: Added full_time_binary: \n"""
        f"""{example} \n""")

    return data_subject
