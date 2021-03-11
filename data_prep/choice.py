import os
import subprocess

import numpy as np
import pandas as pd

from analysis.choice_task.test_clusters import test_transition_clusters
from data_prep.add_variables.aoi import add_fixation_counter, count_fixations_on_trial_level, \
    add_aoi_counts_on_trial_level, add_aoi_et, report_excluded_data_aoi, match_remaining_et_trials, \
    match_remaining_et_runs
from data_prep.add_variables.et_indices import add_et_indices
from utils.data_frames import merge_by_index, merge_by_subject
from utils.path import makedir
from utils.tables import summarize_datasets


def add_variables_to_choice_task_datasets(use_adjusted_et_data=False):

    print('################################### \n'
          'Calculate variables for choice data \n'
          '################################### \n')

    if use_adjusted_et_data:
        print('Using adjusted et data (data_et from' +
              os.path.join('data', 'choice_task', 'adjusted') + '\n')
        data_et = pd.read_csv(
            os.path.join('data', 'choice_task', 'adjusted', 'data_et.csv'))

    else:
        data_et = pd.read_csv(
            os.path.join(
                'data', 'choice_task', 'cleaned', 'data_et.csv'))

    data_trial = pd.read_csv(
        os.path.join(
            'data', 'choice_task', 'cleaned', 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join(
            'data', 'choice_task', 'cleaned', 'data_subject.csv'))

    print('Imported data from ' +
          os.path.join('data', 'choice_task', 'cleaned') + ':')
    summarize_datasets(data_et, data_trial, data_subject)

    # # Information attributes
    data_trial = identify_amount_left(data_trial)
    data_trial = add_choice_options_num(data_trial)
    data_trial = reformat_attributes(data_trial)
    data_trial = top_bottom_attributes(data_trial)
    data_trial['k'] = k(
        data_trial['aLL'], data_trial['aSS'], data_trial['tLL'])

    data_et = merge_by_index(
        data_et, data_trial, 'amountLeft', 'LL_top')

    # Behavioral responses
    data_trial = choice_response_variables(data_trial)
    data_subject = add_mean_choice_rt(data_subject, data_trial)
    data_subject = merge_by_subject(
        data_subject, data_trial,
        'choseLL', 'choseTop', 'LL_top')

    # AOIs
    data_et = add_aoi_et(data_et, use_adjusted_et_data)
    report_excluded_data_aoi(data_et)

    data_trial = match_remaining_et_trials(data_trial, data_et)
    data_subject = match_remaining_et_runs(data_subject, data_et)

    data_et = add_fixation_counter(data_et)

    data_trial = count_fixations_on_trial_level(data_trial, data_et)
    data_trial = add_aoi_counts_on_trial_level(data_trial, data_et)

    data_trial = add_et_indices(data_trial, data_et)

    data_subject = merge_by_subject(
        data_subject, data_trial,
        'attributeIndex', 'optionIndex', 'payneIndex')

    data_trial = test_transition_clusters(data_trial)

    if use_adjusted_et_data:
        data_et.to_csv(
            os.path.join(
                'data', 'choice_task', 'adjusted', 'data_et.csv'),
            index=False, header=True)
        data_trial.to_csv(
            os.path.join(
                'data', 'choice_task', 'adjusted', 'data_trial.csv'),
            index=False, header=True)
        data_subject.to_csv(
            os.path.join(
                'data', 'choice_task', 'adjusted', 'data_subject.csv'),
            index=False, header=True)
    else:
        makedir('data', 'choice_task', 'uncorrected')
        data_et.to_csv(
            os.path.join(
                'data', 'choice_task', 'uncorrected', 'data_et.csv'),
            index=False, header=True)
        data_trial.to_csv(
            os.path.join(
                'data', 'choice_task', 'uncorrected', 'data_trial.csv'),
            index=False, header=True)
        data_subject.to_csv(
            os.path.join(
                'data', 'choice_task', 'uncorrected', 'data_subject.csv'),
            index=False, header=True)
    summarize_datasets(data_et, data_trial, data_subject)


def identify_amount_left(data):
    data['amountLeft'] = 0
    data.loc[
        (data['option_topLeft'].str.contains("\$", regex=True)) |
        (data['option_topLeft'].str.contains("cent", regex=True)),
        'amountLeft'] = 1
    data['amountLeft'].unique()

    print(
        f"""data_trial: Identify amount left: \n"""
        f"""{data.loc[:, ['amountLeft', 'option_topLeft']].head(5)} \n"""
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

    example = data_trial.loc[
        :,
        [
            'option_TL',
            'option_BL',
            'option_TR',
            'option_BR',
            'option_TL_num',
            'option_BL_num',
            'option_TR_num',
            'option_BR_num'
        ]
        ].head(5)

    print(
        f"""data_trial: Add choice_options_num: \n"""
        f"""{example} \n""")

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
    ].sort_values(by='LL_top').head(5)

    print(
        f"""data_trial: Added top and bottom attributes: """
        f"""{example} \n"""
    )

    return data


def choice_response_variables(data):
    # Up-Arrow is 38, Down-Arrow is 40
    data["choseTop"] = 0
    data.loc[(data["key_press"] == 38), "choseTop"] = 1

    data["choseLL"] = 0
    data.loc[(data["choseTop"] == 1) & (data["LL_top"] == 1), "choseLL"] = 1
    data.loc[(data["choseTop"] == 0) & (data["LL_top"] == 0), "choseLL"] = 1

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


def run_et_cluster_correction():
    print('Run cluster correction for eyetracking data. \n')
    os.chdir(os.path.join('data_prep', 'clustering'))

    # noinspection SpellCheckingInspection
    run_matlab = \
        'matlab -wait -nojvm -nosplash -nodesktop -r ' \
        '"init_clustering(14, 0.3, 0.3); exit"'

    subprocess.run(run_matlab, shell=True, check=True)

    os.chdir(os.path.join('..', '..'))
