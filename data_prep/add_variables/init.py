import os

import pandas as pd

from data_prep.add_variables.eye_tracking import add_et_variables
from data_prep.add_variables.subject import add_subject_variables
from data_prep.add_variables.trial import add_trial_variables, add_fps_trial_level, merge_count_by_index
from utils.path import makedir
from utils.tables import summarize_datasets


def global_add_variables_to_datasets():

    print('################################### \n'
          'Create global variables \n'
          '################################### \n')

    data_et = pd.read_csv(
        os.path.join('data', 'all_trials', 'combined', 'data_et.csv'))
    data_trial = pd.read_csv(
        os.path.join('data', 'all_trials', 'combined', 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join('data', 'all_trials', 'combined', 'data_subject.csv'))
    print('Imported from data/all_trials/combined:')
    summarize_datasets(data_et, data_trial, data_subject)

    n_approved_unique = len(data_subject.loc[
                                data_subject['status'] == 'APPROVED',
                                'prolificID'].unique())

    n_approved = len(data_subject.loc[
                     data_subject['status'] == 'APPROVED', :])

    print(f"""Number of approved runs: """
          f"""n={n_approved_unique} unique participants """
          f"""({n_approved} approved IDs, incl. duplicates). \n""")

    data_et = add_et_variables(data_et)
    data_trial = add_trial_variables(data_trial)
    data_trial = merge_count_by_index(data_trial, data_et, 'x')
    data_trial = add_fps_trial_level(data_trial)
    data_subject = add_subject_variables(data_subject, data_trial)

    makedir('data', 'all_trials', 'added_var')
    data_et.to_csv(
        os.path.join('data', 'all_trials', 'added_var', 'data_et.csv'),
        index=False, header=True)

    data_trial.to_csv(
        os.path.join('data', 'all_trials', 'added_var', 'data_trial.csv'),
        index=False, header=True)

    data_subject.to_csv(
        os.path.join('data', 'all_trials', 'added_var', 'data_subject.csv'),
        index=False, header=True)
