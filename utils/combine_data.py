import numpy as np
import pandas as pd


def merge_by_subject(data, large_data, var_name):
    if var_name in data.columns: data = data.drop(columns=[var_name])
    grouped = large_data.groupby(['run_id'])[var_name].mean() \
        .reset_index()
    data = data.merge(grouped, on=['run_id'], how='left')
    return data


def add_var_to_data_et(data_et, source_data, varName):
    if varName in data_et.columns: data_et=data_et.drop(columns=varName)
    data_et = data_et.merge(
        source_data.loc[:, ['run_id', 'trial_index', varName]],
        on=['run_id', 'trial_index'], how='left')
    return data_et


def merge_by_index(data_trial, data_grouped, var_string):
    if var_string in data_trial.columns:
        data_trial = data_trial.drop(columns=[var_string])
    data_trial = data_trial.merge(
        data_grouped, on=['run_id', 'task_index'], how='left')
    return data_trial
