import numpy as np
import pandas as pd


def merge_by_subject(data, data_2, *args):

    for var in [*args]:

        grouped = data_2[['run_id', var]].drop_duplicates()

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


def combine_runs(all_runs, *args):
    for runs in [*args]:
        all_runs = list(
            set(all_runs) |
            set(runs))

    return all_runs
