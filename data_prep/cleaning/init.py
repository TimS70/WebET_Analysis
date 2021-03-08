import os

import pandas as pd

from analysis.dropouts import dropout_analysis
from data_prep.cleaning.drop_na_eye_tracking import drop_na_data_et
from data_prep.cleaning.filter_approved import filter_approved
from data_prep.cleaning.invalid_runs import filter_invalid_runs, clean_runs
from data_prep.cleaning.prolific_ids import clean_prolific_ids, match_ids_with_subjects
from data_prep.cleaning.replace_subject_vars import replace_subject_variables
from utils.path import makedir
from utils.tables import summarize_datasets


def global_cleaning(analyze_dropouts=True):

    data_et = pd.read_csv(
        os.path.join('data', 'added_var', 'data_et.csv'))
    data_trial = pd.read_csv(
        os.path.join('data', 'added_var', 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join('data', 'added_var', 'data_subject.csv'))
    print('Imported from data/added_var:')
    summarize_datasets(data_et, data_trial, data_subject)

    data_et = drop_na_data_et(data_et)
    data_subject = replace_subject_variables(data_subject)

    data_et = filter_approved(data_et, data_subject)
    data_trial = filter_approved(data_trial, data_subject)
    data_subject = filter_approved(data_subject, data_subject)

    data_subject = clean_prolific_ids(data_subject)
    data_trial = match_ids_with_subjects(data_trial, data_subject)
    data_et = match_ids_with_subjects(data_et, data_subject)

    excluded_runs = filter_invalid_runs(
        data_trial, data_et, data_subject)

    data_et = clean_runs(data_et, excluded_runs)
    data_trial = clean_runs(data_trial, excluded_runs)
    data_subject = clean_runs(data_subject, excluded_runs)

    summarize_datasets(data_et, data_trial, data_subject)

    makedir('data', 'cleaned')
    data_et.to_csv(
        os.path.join('data', 'cleaned', 'data_et.csv'),
        index=False, header=True)
    data_trial.to_csv(
        os.path.join('data', 'cleaned', 'data_trial.csv'),
        index=False, header=True)
    data_subject.to_csv(
        os.path.join('data', 'cleaned', 'data_subject.csv'),
        index=False, header=True)
