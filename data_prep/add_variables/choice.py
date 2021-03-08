import os
import subprocess
import pandas as pd

from utils.tables import summarize_datasets


def add_variables_to_choice_task_datasets(use_adjusted_et_data=False):

    print('Adding variables to choice_task... \n')

    if use_adjusted_et_data:
        print('Using adjusted et data \n')
        data_et = pd.read_csv(
            os.path.join('data', 'choice_task', 'adjusted', 'data_et.csv'))

    else:
        data_et = pd.read_csv(
            os.path.join('data', 'choice_task', 'cleaned', 'data_et.csv'))
        data_trial = pd.read_csv(
            os.path.join('data', 'choice_task', 'cleaned', 'data_trial.csv'))
        data_subject = pd.read_csv(
            os.path.join('data', 'choice_task', 'cleaned', 'data_subject.csv'))

    print('Imported from data/choice_task/cleaned: ')
    summarize_datasets(data_et, data_trial, data_subject)


def run_et_cluster_correction():
    print('Run cluster correction for eyetracking data...')
    os.chdir(os.path.join('clustering'))
    print(os.getcwd())

    run_matlab = 'matlab -nojvm -nosplash -nodesktop -r "init_clustering(14, 0.3, 0.3); exit"'

    subprocess.run(run_matlab, shell=True, check=True)

    os.chdir(os.path.join('..'))
