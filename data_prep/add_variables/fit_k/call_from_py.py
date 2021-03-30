import os
import subprocess

import pandas as pd

from utils.combine import merge_by_subject
from utils.save_data import write_csv


def add_log_k(file_origin, file_merge_to):

    print('Fitting discounting parameter log(k) in Matlab. \n')
    path_matlab_fit_k = os.path.join('data_prep', 'add_variables', 'fit_k')
    os.chdir(path_matlab_fit_k)

    # noinspection SpellCheckingInspection
    run_matlab = \
        'matlab -wait -nojvm -nosplash -nodesktop -r "fit_discount_k(' + \
        file_origin + '); exit"'

    subprocess.run(run_matlab, shell=True, check=True)

    os.chdir(os.path.join('../..', '..'))

    root = "C:/Users/User/GitHub/WebET_Analysis"
    log_k = pd.read_csv(os.path.join(path_matlab_fit_k, 'log_k.csv'))

    print('Imported data from ' + file_merge_to + ':')
    data_subject = pd.read_csv(file_merge_to)

    data_subject = merge_by_subject(data_subject, log_k, 'logK', 'noise')
    os.remove(os.path.join(path_matlab_fit_k, 'log_k.csv'))

    missing_values = data_subject.loc[
        pd.isna(data_subject['logK']),
        ['run_id', 'prolificID', 'num_approvals', 'choice_rt', 'choseLL', 'choseTop', 'logK', 'noise']
    ]

    write_csv(missing_values, 'missing_log_k.csv', path_matlab_fit_k)

    print(f"""n={len(data_subject)} participants. """
          f"""{len(missing_values)} missing logK values. \n"""
          f"""{missing_values}""")

    print('Data saved to ' + file_merge_to + ':')
    data_subject.to_csv(os.path.join(file_merge_to), index=False, header=True)

    return data_subject