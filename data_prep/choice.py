import os
import subprocess

import numpy as np
import pandas as pd

from analysis.choice_task.test_clusters import test_transition_clusters
from data_prep.add_variables.aoi import add_fixation_counter, count_fixations_on_trial_level, \
    add_aoi_counts_on_trial_level, add_aoi_et, match_remaining_et_trials, \
    match_remaining_et_runs
from data_prep.add_variables.et_indices import add_et_indices
from utils.data_frames import merge_by_index, merge_mean_by_subject
from utils.path import makedir
from utils.tables import summarize_datasets, load_all_three_datasets, save_all_three_datasets, write_csv


def add_variables_choice():

    print('################################### \n'
          'Add variables for choice data \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'choice_task', 'raw'))

    # Add data from fixation task
    data_subject_fix = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_subject.csv'))
    data_subject = merge_mean_by_subject(data_subject, data_subject_fix, 'offset', 'precision')

    # Information attributes
    data_trial = identify_amount_left(data_trial)
    data_trial = add_choice_options_num(data_trial)
    data_trial = reformat_attributes(data_trial)
    data_trial = data_trial.assign(
        k=k(data_trial['aLL'], data_trial['aSS'], data_trial['tLL']))
    data_trial = top_bottom_attributes(data_trial)

    data_et = merge_by_index(data_et, data_trial, 'amountLeft', 'LL_top')

    # Behavioral responses
    data_trial = choice_response_variables(data_trial)

    data_subject = add_mean_choice_rt(data_subject, data_trial)

    data_subject = merge_mean_by_subject(
        data_subject, data_trial, 'choseLL', 'choseTop', 'LL_top')

    # AOIs
    data_et = add_aoi_et(data_et)
    data_trial = match_remaining_et_trials(data_trial, data_et)
    data_trial = add_aoi_counts_on_trial_level(data_trial, data_et)
    data_trial = add_et_indices(data_trial, data_et)

    data_subject = add_et_indices_subject(
        data_subject, data_trial, 5)

    data_et = add_fixation_counter(data_et)

    data_trial = count_fixations_on_trial_level(data_trial, data_et)
    data_trial = test_transition_clusters(data_trial)

    save_all_three_datasets(
        data_et, data_trial, data_subject,
        os.path.join('data', 'choice_task', 'added_var'))


def identify_amount_left(data):
    data['amountLeft'] = 0
    data.loc[
        (data['option_topLeft'].str.contains("\$", regex=True)) |
        (data['option_topLeft'].str.contains("cent", regex=True)),
        'amountLeft'] = 1
    data['amountLeft'].unique()

    grouped_test = data.groupby(
        ['run_id', 'amountLeft'],
        as_index=False).agg(
        n=('trial_index', 'count'),
        max_task_nr=('withinTaskIndex', 'max'),
        min_task_nr=('withinTaskIndex', 'min'),
    )

    example = data.loc[:,
             ['amountLeft', 'option_topLeft', 'option_bottomLeft',
              'option_topRight', 'option_bottomRight']] \
        .sort_values(by='amountLeft')

    print(
        f"""data_trial: Identify amount left: \n"""
        f"""{example} \n"""
        f"""{grouped_test} \n"""
    )
    return data


def add_choice_options_num(data_trial):
    data_trial = data_trial \
        .rename(columns={
            'option_topLeft': 'option_TL',
            'option_bottomLeft': 'option_BL',
            'option_topRight': 'option_TR',
            'option_bottomRight': 'option_BR'})

    variables = [
        'option_TL',
        'option_BL',
        'option_TR',
        'option_BR'
    ]
    for var in variables:
        data_trial = choice_options_to_numeric(data_trial, var)

    print(f"""data_trial: Add choice_options_num. \n""")

    return data_trial


def choice_options_to_numeric(data, var_name):
    data[var_name + '_num'] = data[var_name]
    data[var_name + '_num'] = data[var_name + '_num'] \
        .replace(['Today', 'Tomorrow', '7 days',
                  '15 days', '30 days', '90 days',
                  '180 days'],
                 [0, 1, 7, 15, 30, 90, 180]) \
        .replace({'\$': ''}, regex=True) \
        .replace('50 cent', 0.5) \
        .astype(float)

    return data


def reformat_attributes(data):
    data['aSS'] = 0
    data.loc[data['amountLeft'] == 1, 'aSS'] = \
        data.loc[
            data['amountLeft'] == 1,
            ["option_TL_num", "option_BL_num"]
        ].values.min(1)
    data.loc[data['amountLeft'] == 0, 'aSS'] = \
        data.loc[
            data['amountLeft'] == 0,
            ["option_TR_num", "option_BR_num"]
        ].values.min(1)

    data['aLL'] = 0
    data.loc[data['amountLeft'] == 1, 'aLL'] = \
        data.loc[
            data['amountLeft'] == 1,
            ["option_TL_num", "option_BL_num"]
        ].values.max(1)
    data.loc[data['amountLeft'] == 0, 'aLL'] = \
        data.loc[
            data['amountLeft'] == 0,
            ["option_TR_num", "option_BR_num"]
        ].values.max(1)

    data.loc[:, "tSS"] = 0

    data['tLL'] = 0
    data.loc[data['amountLeft'] == 1, 'tLL'] = \
        data.loc[
            data['amountLeft'] == 1,
            ["option_TR_num", "option_BR_num"]
        ].values.max(1)
    data.loc[data['amountLeft'] == 0, 'tLL'] = \
        data.loc[
            data['amountLeft'] == 0,
            ["option_TL_num", "option_BL_num"]
        ].values.max(1)

    # noinspection PyUnresolvedReferences
    data['LL_top'] = (data["option_TL_num"] > data["option_BL_num"]).astype(int)

    print('data_trial: Identified information attributes: ')
    print('aLL values: ' + str(np.sort(data['aLL'].unique())))
    print('aSS values: ' + str(np.sort(data['aSS'].unique())))
    print('tLL values: ' + str(np.sort(data['tLL'].unique())))
    print('tSS values: ' + str(np.sort(data['tSS'].unique())) + '\n')

    return data


def top_bottom_attributes(data):
    data['aT'] = data['LL_top'] * data['aLL'] + \
        (1-data['LL_top']) * data['aSS']
    data['aB'] = (1-data['LL_top']) * data['aLL'] + \
        data['LL_top'] * data['aSS']
    data['tT'] = data['LL_top'] * data['tLL'] + \
        (1-data['LL_top']) * data['tSS']
    data['tB'] = (1-data['LL_top']) * data['tLL'] + \
        data['LL_top'] * data['tSS']

    example = data.loc[
        :,
        ['aT', 'tT', 'aB', 'tB', 'LL_top']
    ].sort_values(by='LL_top')

    grouped_test = data.groupby(
        ['run_id', 'LL_top'],
        as_index=False).agg(
            n=('trial_index', 'count'),
            max_trial=('withinTaskIndex', 'max'),
            aT_min=('aT', 'min'),
            aT_max=('aT', 'max'),
            aB_min=('aB', 'min'),
            aB_max=('aB', 'max'),
    )

    print(
        f"""data_trial: Added top and bottom attributes: \n"""
        f"""{example} \n"""
        f"""{grouped_test} \n""")

    return data


def choice_response_variables(data):
    # Up-Arrow is 38, Down-Arrow is 40
    data["choseTop"] = 0
    data.loc[(data["key_press"] == 38), "choseTop"] = 1

    data["choseLL"] = 0
    data.loc[(data["choseTop"] == 1) & (data["LL_top"] == 1), "choseLL"] = 1
    data.loc[(data["choseTop"] == 0) & (data["LL_top"] == 0), "choseLL"] = 1

    print(
        f"""Add choice response variables \n"""
        f"""{data.loc[:, 
             ['key_press', 'LL_top', 'choseTop', 'choseLL']]} \n"""
    )
    return data


def k(a_ll, a_ss, t_ll):
    return ((a_ll / a_ss) - 1) / t_ll


def add_mean_choice_rt(data_subject, data_trial):
    grouped = data_trial.groupby(['run_id'])['trial_duration_exact'].mean() \
        .reset_index() \
        .rename(columns={'trial_duration_exact': 'choice_rt'})

    if 'choice_rt' in data_subject.columns:
        data_subject = data_subject.drop(columns=['choice_rt'])
    data_subject = data_subject.merge(grouped, on='run_id', how='left')

    print(
        f"""Added choice_rt: \n"""
        f"""{data_subject['choice_rt'].describe()}\n"""
    )

    return data_subject


def add_et_indices_subject(data_subject, data_trial,
                           min_required_count):

    grouped = data_trial.groupby(
        ['run_id'],
        as_index=False).agg(
        attributeIndex=('attributeIndex', 'mean'),
        attributeIndex_n=('attributeIndex', 'count'),

        optionIndex=('optionIndex', 'mean'),
        optionIndex_n=('optionIndex', 'count'),

        payneIndex=('payneIndex', 'mean'),
        payneIndex_n=('payneIndex', 'count'),
    )

    print(
        f"""Aggregate ET indices on subject level. \n"""
        f"""Require >= {min_required_count} valid trials to aggregate """
        f"""on subject level. \n""")

    grouped.loc[
        grouped['attributeIndex_n'] < min_required_count,
        'attributeIndex'] = np.nan
    grouped.loc[
        grouped['optionIndex_n'] < min_required_count,
        'optionIndex'] = np.nan
    grouped.loc[
        grouped['payneIndex_n'] < min_required_count,
        'payneIndex'] = np.nan

    data_subject = merge_mean_by_subject(
        data_subject, grouped,
        'attributeIndex', 'optionIndex', 'payneIndex')

    print(
        f"""ET indices on subject level: \n"""
        f"""{data_subject[['attributeIndex', 'optionIndex', 
                           'payneIndex']].describe()} \n"""
    )

    return data_subject


def add_log_k():

    print('Fitting log(k) in Matlab. \n')
    os.chdir(os.path.join('data_prep', 'fit_k'))

    # noinspection SpellCheckingInspection
    run_matlab = \
        'matlab -wait -nojvm -nosplash -nodesktop -r "fit_discount_k(); exit"'

    subprocess.run(run_matlab, shell=True, check=True)

    os.chdir(os.path.join('..', '..'))

    root = "C:/Users/User/GitHub/WebET_Analysis"
    log_k = pd.read_csv(os.path.join(root, 'data', 'choice_task', 'logK.csv'))

    path = os.path.join('data', 'choice_task', 'added_var')
    print('Imported data from ' + path + ':')
    data_subject = pd.read_csv(os.path.join(
        path, 'data_subject.csv'))

    data_subject = merge_mean_by_subject(
        data_subject, log_k, 'logK', 'noise')

    missing_values = data_subject.loc[
        pd.isna(data_subject['logK']),
        ['run_id', 'prolificID', 'num_approvals', 'choice_rt', 'choseLL', 'choseTop', 'logK', 'noise']
    ]

    write_csv(missing_values, 'missing_log_k.csv',
        'data', 'choice_task')

    print(
        f"""n={len(data_subject)} participants. """
        f"""{len(missing_values)} missing logK values. \n"""
        f"""{missing_values}""")

    print('Data saved to ' + path + ':')

    data_subject.to_csv(
        os.path.join(path, 'data_subject.csv'),
        index=False, header=True)


    return data_subject


def run_et_cluster_correction():
    print('Run cluster correction for eyetracking data. \n')
    os.chdir(os.path.join('data_prep', 'clustering'))

    # noinspection SpellCheckingInspection
    run_matlab = \
        'matlab -wait -nojvm -nosplash -nodesktop -r ' \
        '"init_clustering(14, 0.3, 0.3); exit"'

    subprocess.run(run_matlab, shell=True, check=True)

    os.chdir(os.path.join('..', '..'))
