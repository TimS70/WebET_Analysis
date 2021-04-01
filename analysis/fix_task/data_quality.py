import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils.combine import merge_by_index
from visualize.all_tasks import save_plot
from utils.save_data import write_csv


def group_within_task_index(data, group_var, var_name):
    df_m = data.groupby(
        [group_var, 'withinTaskIndex'])[var_name].median() \
        .reset_index() \
        .rename(columns={var_name: var_name + '_median'}) \
        .reset_index()

    data = data.merge(df_m, on=[group_var, 'withinTaskIndex'], how='left')
    data['above_median'] = data[var_name] > data[var_name + '_median']

    df_std_upper = data.loc[data['above_median'] == 1, :] \
        .groupby([group_var, 'withinTaskIndex'])[var_name].median() \
        .reset_index() \
        .rename(columns={var_name: var_name + '_std_upper'}) \
        .reset_index()
    df_std_lower = data.loc[data['above_median'] == 0, :] \
        .groupby([group_var, 'withinTaskIndex'])[var_name].median() \
        .reset_index() \
        .rename(columns={var_name: var_name + '_std_lower'}) \
        .reset_index()

    output = pd.concat([
        df_m,
        df_std_upper[var_name + '_std_upper'],
        df_std_lower[var_name + '_std_lower']
    ], axis=1)

    return output



def compare_conditions_subject(data_subject, data_trial_fix, outcome):
    data_subject = separate_outcomes_by_condition(
        data_subject, data_trial_fix, outcome, 'chin')

    data_subject = separate_outcomes_by_condition(
        data_subject, data_trial_fix, outcome, 'glasses_binary')

    summary = data_subject.loc[
              :,
              [
                  outcome, (outcome + '_chin_0'),
                  (outcome + '_chin_1'),
                  (outcome + '_glasses_binary_0'),
                  (outcome + '_glasses_binary_1')
              ]
              ].describe()

    write_csv(
        summary,
        (outcome + '_compare_glasses_chin_subject.csv'),
        'results', 'tables', 'fix_task')


def separate_outcomes_by_condition(data, large_data,
                                   var_name, var_condition):
    var_cond_0 = var_name + '_' + var_condition + '_0'
    var_cond_1 = var_name + '_' + var_condition + '_1'

    if var_cond_0 in data.columns:
        data = data.drop(columns=[var_cond_0])
    if var_cond_1 in data.columns:
        data = data.drop(columns=[var_cond_1])

    grouped = large_data \
        .groupby(['run_id', var_condition])[var_name].mean() \
        .reset_index() \
        .pivot(index='run_id',
               columns=var_condition,
               values=var_name) \
        .reset_index() \
        .rename(columns={0.0: var_cond_0, 1.0: var_cond_1})
    data = data.merge(
        grouped.loc[:, ['run_id', var_cond_0, var_cond_1]],
        on='run_id',
        how='left')

    return data
