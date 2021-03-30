import os
import subprocess

import pandas as pd

from utils.combine import merge_by_subject
from utils.save_data import write_csv


def add_log_k(file_trial_input, file_subjects_to_merge, path):

    path_matlab_fit_k = os.path.join('data_prep', 'add_variables', 'fit_k')
    path_input = os.path.join(path, file_trial_input)
    path_to_merge = os.path.join(path, file_subjects_to_merge)

    # noinspection SpellCheckingInspection
    run_matlab = \
        f"""matlab -wait -nojvm -nosplash -nodesktop -r "fit_discount_k('""" + \
        path_input + """', '""" + path + """'); exit"""

    print(f"""Fitting discounting parameter log(k) in Matlab. \n"""
          f"""Run Matlab from console: \n"""
          f"""{run_matlab} \n""")

    os.chdir(path_matlab_fit_k)
    subprocess.run(run_matlab, shell=True, check=True)
    os.chdir(os.path.join('../..', '..'))

    root = "C:/Users/User/GitHub/WebET_Analysis"
    log_k = pd.read_csv(os.path.join(path, 'log_k.csv'))

    print('Imported data from ' + path_to_merge + ':')
    data_subject = pd.read_csv(path_to_merge)

    data_subject = merge_by_subject(data_subject, log_k, 'logK', 'noise')

    missing_values = data_subject.loc[
        pd.isna(data_subject['logK']),
        ['run_id', 'prolificID', 'choice_rt', 'choseLL', 'choseTop', 'logK',
         'noise']]

    if len(missing_values) > 0:
        print(f"""n={len(data_subject)} participants. """
              f"""{len(missing_values)} missing logK values. \n"""
              f"""{missing_values}""")

        write_csv(missing_values, 'missing_log_k.csv', path)
    else:
        print('All participants could be fitted to hyperbolic discounting')

    print('Data saved to ' + path_to_merge + ':')
    data_subject.to_csv(os.path.join(path_to_merge), index=False, header=True)

    return data_subject