import os
import subprocess

import pandas as pd

from utils.combine_frames import merge_mean_by_subject
from utils.save_data import write_csv


def add_log_k():

    print('Fitting log(add_k) in Matlab. \n')
    os.chdir(os.path.join('data_prep', 'fit_k'))

    # noinspection SpellCheckingInspection
    run_matlab = \
        'matlab -wait -nojvm -nosplash -nodesktop -r "fit_discount_k(); exit"'

    subprocess.run(run_matlab, shell=True, check=True)

    os.chdir(os.path.join('../..', '..'))

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