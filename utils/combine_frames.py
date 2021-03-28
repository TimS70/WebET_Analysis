import numpy as np
import pandas as pd


def merge_by_subject(data, data_2, *args):

    for var in [*args]:

        grouped = data_2[['run_id', var]].drop_duplicates()

        if var in data.columns:
            data = data.drop(columns=[var])

        data = data.merge(grouped, on=['run_id'], how='left')

    return data


def merge_mean_by_subject(data, large_data, *args):

    for var in [*args]:

        grouped = large_data.groupby(
            ['run_id'],
            as_index=False)[var].mean()

        if var in data.columns:
            data = data.drop(columns=[var])

        data = data.merge(grouped, on=['run_id'], how='left')

    return data


def merge_by_index(data_et, source_data, *args):

    for var in [*args]:

        if var in data_et.columns:
            data_et = data_et.drop(columns=var)

        data_et = data_et.merge(
            source_data[['run_id', 'trial_index', var]],
            on=['run_id', 'trial_index'], how='left')

    return data_et


def merge_mean_by_index(data, large_data, *args):

    for var in [*args]:

        if var in data.columns:
            data = data.drop(columns=[var])
        grouped = large_data.groupby(['run_id', 'trial_index'])[var].mean() \
            .reset_index()
        data = data.merge(grouped, on=['run_id', 'trial_index'], how='left')

    return data