import numpy as np
import pandas as pd


def merge_by_subject(data, large_data, var_name):
    if var_name in data.columns: data = data.drop(columns=[var_name])
    grouped = large_data.groupby(['run_id'])[var_name].mean() \
        .reset_index()
    data = data.merge(grouped, on=['run_id'], how='left')
    return data