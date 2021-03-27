import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils.combine_frames import merge_by_index
from visualize.all_tasks import save_plot
from utils.save_data import write_csv


def outcome_over_trials(data_trial, outcome):
    data_plot = data_trial.copy()

    print(data_trial.loc[
              pd.notna(data_trial[outcome]),
              'task_nr'].unique())
    data_plot['task_nr'] = data_plot['task_nr'] \
        .replace([1, 2, 3], [0, 1, 1])

    data_plot = group_within_task_index(
        data_plot.loc[data_plot['fixTask'] == 1, :],
        'task_nr',
        outcome)

    plt.style.use('seaborn-whitegrid')
    fig, ax = plt.subplots(1, 2, sharey=True, figsize=(15, 6))
    fig.suptitle('Task 1 vs. Task 2')

    ax[0].set_ylim(0, 1)

    for i in [0, 1]:
        data = data_plot.loc[data_plot['task_nr'] == i, :]
        ax[i].errorbar(
            x=data['withinTaskIndex'],
            y=data[(outcome + '_median')],
            yerr=[data[(outcome + '_std_lower')],
                  data[(outcome + '_std_upper')]],
            fmt='^k:',
            capsize=5
        )

    save_plot((outcome + '_vs_trials.png'),
              'results', 'plots', 'fix_task')
    plt.close()


def outcome_over_trials_vs_chin(data_trial, outcome):
    data_plot = group_within_task_index(
        data_trial.loc[data_trial['fixTask'] == 1, :],
        'chin',
        outcome)

    plt.style.use('seaborn-whitegrid')
    fig, ax = plt.subplots(1, 2, sharey=True, figsize=(15, 6))
    fig.suptitle('chin==0 vs. chin==1')

    ax[0].set_ylim(0, 1)

    for i in [0, 1]:
        data = data_plot.loc[data_plot['chin'] == i, :]
        ax[i].errorbar(
            x=data['withinTaskIndex'],
            y=data[(outcome + '_median')],
            yerr=[data[(outcome + '_std_lower')],
                  data[(outcome + '_std_upper')]],
            fmt='^k:',
            capsize=5)

    save_plot((outcome + '_vs_chin_vs_trials.png'),
              'results', 'plots', 'fix_task', outcome)
    plt.close()


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


def grand_mean_offset(data_et_fix, data_trial):
    grouped = data_et_fix.groupby(
        ['run_id', 'trial_index'],
        as_index=False)[['x', 'y']].mean() \
        .rename(columns={'x': 'x_mean', 'y': 'y_mean'})

    data_trial = merge_by_index(data_trial, grouped, 'x_mean')
    data_trial = merge_by_index(data_trial, grouped, 'y_mean')

    data_trial['x_mean_px'] = \
        data_trial['x_mean'] * data_trial['window_width']
    data_trial['y_mean_px'] = \
        data_trial['y_mean'] * data_trial['window_height']

    data_trial['grand_deviation'] = euclidean_distance(
        data_trial['x_mean'], data_trial['x_pos'],
        data_trial['y_mean'], data_trial['y_pos'])

    summary = data_trial['grand_deviation'].describe()

    write_csv(
        summary,
        'grand_mean.csv',
        'results', 'tables', 'fix_task')

    print(
        f"""Grand mean deviation: \n"""
        f"""{summary} \n""")

    grand_mean_positions = data_trial \
        .loc[data_trial['fixTask'] == 1, :] \
        .groupby(
            ['x_pos', 'y_pos'],
            as_index=False).agg(
            grand_dev=('grand_deviation', 'mean'),
            grand_dev_std=('grand_deviation', 'std'))

    write_csv(
        grand_mean_positions,
        'grand_mean_positions.csv',
        'results', 'tables', 'fix_task')

    font_size = 15
    plt.rcParams.update({'font.size': font_size})

    plt.hist(data_trial['grand_deviation'], bins=20)
    plt.title('Grand mean deviation')
    save_plot('grand_mean.png', 'results', 'plots',
              'fix_task', 'offset')
    plt.close()

    return data_trial


def euclidean_distance(x, x_target, y, y_target):
    x_diff = x - x_target
    y_diff = y - y_target
    output = np.sqrt(x_diff ** 2 + y_diff ** 2)

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
