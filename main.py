import os
import pandas as pd

from prep.load.data_subject_prolific import create_data_subject
from prep.load.data_subject_prolific import create_data_prolific
from prep.load.eye_tracking import create_et_data
from prep.load.prolific import combine_prolific_data
from prep.load.trial import create_trial_data

from prep.add_variables.eye_tracking import add_et_variables
from prep.add_variables.trial import add_trial_variables
from prep.add_variables.trial import add_fps_trial_level
from prep.add_variables.subject import add_subject_variables

from prep.replace.subject import clean_subject_variables
from prep.exclude_subjects.exclude import exclude_na_data_et

from utils.tables import summarize_datasets


def main(new_data=False):
    if new_data:
        # Create datasets from Prolific data
        data_combined = combine_prolific_data(30)
        data_trial = create_trial_data(data_combined)
        data_et = create_et_data(data_combined)
        data_subject = create_data_subject(data_combined)
        create_data_prolific(data_subject)
        summarize_datasets(data_et, data_trial, data_subject)

    else:
        data_et = pd.read_csv(
            os.path.join('data', 'combined', 'data_et.csv'))
        data_trial = pd.read_csv(
            os.path.join('data', 'combined', 'data_trial.csv'))
        data_subject = pd.read_csv(
            os.path.join('data', 'combined', 'data_subject.csv'))
        print('Imported from data/combined:')
        summarize_datasets(data_et, data_trial, data_subject)

    # Add variables
    data_et = add_et_variables(data_et)
    data_trial = add_trial_variables(data_trial)
    data_trial = add_fps_trial_level(data_trial, data_et)
    data_subject = add_subject_variables(data_subject, data_trial)

    # Cleaning
    # data_subject = clean_subject_variables(data_subject)
    # data_et = exclude_na_data_et(data_et)


if __name__ == '__main__':
    main(new_data=False)
