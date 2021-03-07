import pandas as pd

from utils.tables import summarize_datasets


def add_variables_to_choice_datasets(
        use_adjusted_et_data = False):

    if use_adjusted_et_data:
        print('Using adjusted et data \n')
        data_et = pd.read_csv(
            r'C:/Users/User/GitHub/WebET_Analysis/data_jupyter/choice_task/adjusted/data_et.csv')

    else:
    data_et = pd.read_csv(
        r'C:/Users/User/GitHub/WebET_Analysis/data_jupyter/choice_task/cleaned/data_et.csv')

    data_trial = pd.read_csv(
        r'C:/Users/User/GitHub/WebET_Analysis/data_jupyter/choice_task/cleaned/data_trial.csv')
    data_subject = pd.read_csv(
        r'C:/Users/User/GitHub/WebET_Analysis/data_jupyter/choice_task/cleaned/data_subject.csv')

    print('Imported from data/combined: ')
    summarize_datasets(data_et, data_trial, data_subject)