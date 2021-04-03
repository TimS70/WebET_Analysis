import os
import subprocess

import numpy as np
import pandas as pd

from utils.combine import merge_by_subject
from utils.save_data import write_csv


def load_data():
    root = r'C:\Users\User\GitHub\WebET_Analysis'
    path = os.path.join(root, 'data', 'amasino', 'raw')

    # x, y starts at top-left (0, 0)
    data_et = pd.read_csv(
        os.path.join(path, 'amasinoEtAl_ET_rep.csv'),
        names=['run_id', 'withinTaskIndex', 'x', 'y', 'fix_count'])

    data_trial = pd.read_csv(
        os.path.join(path, 'amasinoEtAl_behavior_rep.csv'),
        names=['run_id', 'aSS', 'aLL', 'tSS', 'tLL', 'choseLL', 'rt',
               'LL_top', 'condition'])

    print('Imported data from ' + path + ':')

    grouped_n_trials_by_id = data_et.groupby(['run_id'], as_index=False).agg(
        n_trials=('withinTaskIndex', 'nunique'))

    summary = pd.DataFrame({
        'dataset': [
            'data_et',
            'data_trial'],
        'runs': [
            len(data_et['run_id'].unique()),
            len(data_trial['run_id'].unique())],
        'n_trials': [
            grouped_n_trials_by_id['n_trials'].sum(),
            len(data_trial)]
        })
    print(f"""{summary} \n""")

    return data_et, data_trial


def add_trial_index(data_trial):
    data_trial['trial_index'] = np.nan

    for run in data_trial['run_id'].unique():
        data_trial.loc[data_trial['run_id'] == run, 'trial_index'] = \
            np.arange(1, sum(data_trial['run_id']==run)+1)

    print(f"""Added trial_index: \n"""
          f"""{data_trial[['run_id', 'trial_index']]} \n""")

    return data_trial


def add_choseTop(data):
    data["choseTop"] = 0
    data.loc[(data["choseLL"] == 1) & (data["LL_top"] == 1),
             "choseTop"] = 1
    data.loc[(data["choseLL"] == 0) & (data["LL_top"] == 0),
             "choseTop"] = 1

    print(
        f"""Add choseTop variables \n"""
        f"""{data.loc[:, 
             ['choseLL', 'LL_top', 'choseTop']]} \n"""
    )
    return data


def add_log_k(data_subject, data_trial):
    print('Fitting log(add_k) in Matlab. \n')
    os.chdir(os.path.join('amasino', 'fit_k'))

    write_csv(data=data_trial,
              file_name='data_trial.csv',
              path=os.path.join('data', 'amasino', 'added_var'))

    # noinspection SpellCheckingInspection
    run_matlab = \
        'matlab -wait -nojvm -nosplash -nodesktop -r "fit_discount_k(); exit"'

    subprocess.run(run_matlab, shell=True, check=True)

    os.chdir(os.path.join('../..', '..'))

    root = "C:/Users/User/GitHub/WebET_Analysis"
    log_k = pd.read_csv(os.path.join(root, 'data', 'amasino', 'logK.csv'))

    data_subject = merge_by_subject(
        data_subject, log_k, 'logK', 'noise')

    missing_values = data_subject.loc[
        pd.isna(data_subject['logK']),
        ['run_id', 'rt', 'choseLL', 'LL_top', 'logK', 'noise']]

    write_csv(data=missing_values, file_name='missing_log_k.csv',
              path=os.path.join('data', 'amasino'))

    print(f"""n={len(data_subject)} participants. """
          f"""{len(missing_values)} missing logK values. \n"""
          f"""{missing_values}""")

    return data_subject


def add_choice_options(data_trial):
    data_trial['option_TL'] = \
        (data_trial['LL_top']) * (
            (data_trial['amountLeft']) * data_trial['aLL'] +
            (1-data_trial['amountLeft']) * data_trial['tLL']) + \
        (1-data_trial['LL_top']) * (
            data_trial['amountLeft'] * data_trial['aSS'] +
            (1-data_trial['amountLeft']) * data_trial['tSS'])

    data_trial['option_TR'] = \
        (data_trial['LL_top']) * (
            (1-data_trial['amountLeft']) * data_trial['aLL'] +
            (data_trial['amountLeft']) * data_trial['tLL']) + \
        (1-data_trial['LL_top']) * (
            (1-data_trial['amountLeft']) * data_trial['aSS'] +
            (data_trial['amountLeft']) * data_trial['tSS'])

    data_trial['option_BL'] = \
        (1-data_trial['LL_top']) * (
            (data_trial['amountLeft']) * data_trial['aLL'] +
            (1-data_trial['amountLeft']) * data_trial['tLL']) + \
        (data_trial['LL_top']) * (
            (data_trial['amountLeft']) * data_trial['aSS'] +
            (1-data_trial['amountLeft']) * data_trial['tSS'])

    data_trial['option_BR'] = \
        (1-data_trial['LL_top']) * (
            (1-data_trial['amountLeft']) * data_trial['aLL'] +
            (data_trial['amountLeft']) * data_trial['tLL']) + \
        (data_trial['LL_top']) * (
            (1-data_trial['amountLeft']) * data_trial['aSS'] +
            (data_trial['amountLeft']) * data_trial['tSS'])

    print(f"""Added choice options: \n"""
          f"""{data_trial[['LL_top', 'amountLeft', 
                           'aLL', 'tLL', 'aSS', 'tSS', 
                           'option_TL', 'option_TR',
                           'option_BL', 'option_BR']].head()} \n""")

    return data_trial