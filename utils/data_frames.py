import numpy as np
import pandas as pd


def merge_by_subject(data, large_data, *args):

    for var in [*args]:

        grouped = large_data.groupby(['run_id'])[var].mean() \
            .reset_index()

        if var in data.columns:
            data = data.drop(columns=[var])

        data = data.merge(grouped, on=['run_id'], how='left')

    return data


def add_var_to_data_et(data_et, source_data, *args):

    for var in [*args]:

        if var in data_et.columns:
            data_et = data_et.drop(columns=var)

        data_et = data_et.merge(
            source_data.loc[:, ['run_id', 'trial_index', var]],
            on=['run_id', 'trial_index'], how='left')

    return data_et


def merge_by_index(data_trial, data_grouped, var_string):
    if var_string in data_trial.columns:
        data_trial = data_trial.drop(columns=[var_string])
    data_trial = data_trial.merge(
        data_grouped, on=['run_id', 'trial_index'], how='left')
    return data_trial


def merge_mean_by_index(data, large_data, *args):

    for var in [*args]:

        if var in data.columns:
            data = data.drop(columns=[var])
        grouped = large_data.groupby(['run_id', 'trial_index'])[var].mean() \
            .reset_index()
        data = data.merge(grouped, on=['run_id', 'trial_index'], how='left')

    return data