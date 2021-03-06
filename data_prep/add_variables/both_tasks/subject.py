import datetime
import os

import matplotlib.pyplot as plt
import pandas as pd

from tqdm import tqdm

from utils.combine import merge_by_subject
from visualize.all_tasks import save_plot
import numpy as np


def add_fps_subject_level(data_subject, data_trial):
    grouped = data_trial \
        .groupby(['run_id'], as_index=False) \
        .agg(fps=('fps', 'mean'))
    data_subject = merge_by_subject(data_subject, grouped, 'fps')

    plt.hist(data_subject['fps'], bins=20)
    plt.rc('font', size=10)
    save_plot(file_name='fps_participants.png',
              path=os.path.join('results', 'plots', 'fps'))
    plt.close()

    return data_subject


def add_max_trials(data_subject, data_trial):
    grouped = data_trial \
        .groupby(['run_id'], as_index=False) \
        .agg(max_trial=('trial_index', 'max'))

    data_subject = merge_by_subject(data_subject, grouped, 'max_trial')

    example = data_subject[['run_id', 'prolificID', 'max_trial']].head(5)
    print(f"""data_subject: Added max_trial: \n """
          f"""{example} \n""")

    return data_subject


def add_window(data_subject, data_trial):
    grouped = data_trial \
        .groupby(["run_id"], as_index=False) \
        .agg(window_x=('window_width', 'max'),
             window_y=('window_height', 'max'))

    grouped['window'] = np.sqrt(
        grouped['window_x'] ** 2 + grouped['window_y'] ** 2)

    data_subject = merge_by_subject(data_subject, grouped,
                                    'window', 'window_x', 'window_y')

    return data_subject


def add_glasses_binary(data_subject):
    data_subject['glasses_binary'] = data_subject['sight'] \
        .replace({'contactLenses': 0,
                  'glasses': 1,
                  'notCorrected': 0,
                  'perfectSight': 0})

    n_missing = len(data_subject.loc[
                    pd.isna(data_subject['glasses_binary']), :])

    example = pd.crosstab(
        index=data_subject['glasses_binary'],
        columns="count")

    print(
        f"""\n"""
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
    data_subject['employment_status'] = data_subject['Employment Status'] \
        .replace({
            """Not in paid work (e.g. homemaker', 'retired or disabled)""":
                'not_in_paid_work',
            'DATA EXPIRED': 'Other',
            'Unemployed (and job seeking)': 'not_in_paid_work',
            'Due to start a new job within the next month': 'Other'})

    example = pd.crosstab(
        index=data_subject['employment_status'],
        columns="count")

    print(
        f"""data_subject: Added employment_status: \n"""
        f"""{example} \n""")

    return data_subject


def add_full_time_binary(data_subject):
    data_subject['fullTime_binary'] = data_subject['Employment Status'] \
        .replace([
            'Other', 'Part-Time',
            "Not in paid work (e.g. homemaker', 'retired or disabled)",
            'Unemployed (and job seeking)', 'DATA EXPIRED',
            'Due to start a new job within the next month'], 0) \
        .replace(['Full-Time'], 1)

    example = pd.crosstab(
        index=data_subject['fullTime_binary'],
        columns="count")

    print(
        f"""data_subject: Added full_time_binary: \n"""
        f"""{example} \n""")

    return data_subject
