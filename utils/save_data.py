import os

import pandas as pd

from utils.path import makedir


def load_all_three_datasets(path):
    data_et = pd.read_csv(os.path.join(path, 'data_et.csv'))
    data_trial = pd.read_csv(os.path.join(path, 'data_trial.csv'))
    data_subject = pd.read_csv(os.path.join(path, 'data_subject.csv'))

    print('\nImported data from ' + path + ':')

    if 'prolificID' in data_trial.columns:
        summarize_datasets(data_et, data_trial, data_subject)

    return data_et, data_trial, data_subject


def save_all_three_datasets(data_et, data_trial, data_subject, path):
    print('\nSave data to ' + path + ':')

    makedir(path)

    data_et.to_csv(os.path.join(path, 'data_et.csv'),
                   index=False, header=True)
    data_trial.to_csv(os.path.join(path, 'data_trial.csv'),
                      index=False, header=True)
    data_subject.to_csv(os.path.join(path, 'data_subject.csv'),
                        index=False, header=True)

    if 'prolificID' in data_trial.columns:
        summarize_datasets(data_et, data_trial, data_subject)


def summarize_datasets(data_et, data_trial, data_subject):
    et_trial_count = data_et \
        .groupby(['run_id', 'trial_index'], as_index=False) \
        .agg(x=('x', 'count')) \
        .loc[:, 'trial_index'].count()

    summary = pd.DataFrame({
        'dataset': [
            'data_et',
            'data_trial',
            'data_subject'],
        'prolific_ids': [
            '-',
            len(data_trial['prolificID'].unique()),
            len(data_subject['prolificID'].unique())],
        'runs': [
            len(data_et['run_id'].unique()),
            len(data_trial['run_id'].unique()),
            len(data_subject['run_id'].unique())],
        'n_trials': [
            et_trial_count,
            len(data_trial),
            '-']
        })
    print(f"""{summary} \n""")


def write_csv(data_frame, file_name, *args):
    makedir(*args)
    path = os.path.join(*args)
    data_frame.to_csv(os.path.join(path, file_name), index=False)
    print(
        f"""File '{file_name}' saved in {path} \n""")
