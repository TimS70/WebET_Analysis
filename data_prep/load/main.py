import os

import pandas as pd

from data_prep.load.data_subject_prolific import create_data_subject, \
    create_data_prolific, add_and_filter_prolific
from data_prep.load.eye_tracking import create_et_data
from data_prep.load.prolific import combine_cognition_data
from data_prep.load.trial import create_trial_data
from utils.save_data import save_all_three_datasets, write_csv


def create_datasets_from_cognition(path_origin, path_target):
    # Create datasets from Prolific data
    data_combined = combine_cognition_data(path_origin)
    data_trial = create_trial_data(data_combined)
    data_et = create_et_data(data_combined)
    data_subject = create_data_subject(data_combined)

    save_all_three_datasets(
        data_et, data_trial, data_subject, path_target)


def integrate_prolific_data(path_origin, path_target):
    data_subject = pd.read_csv(os.path.join(path_origin, 'data_subject'))

    data_subject = add_and_filter_prolific(data_subject)

    write_csv(data_subject, 'data_subject.csv', path_target)

    data_prolific = create_data_prolific(data_subject)

    write_csv(data_prolific, 'data_prolific.csv', path_target)
