from data_prep.load.data_subject_prolific import create_data_subject, create_data_prolific
from data_prep.load.eye_tracking import create_et_data
from data_prep.load.prolific import combine_cognition_data
from data_prep.load.trial import create_trial_data
from utils.save_data import summarize_datasets


def create_datasets_from_cognition():
    # Create datasets from Prolific data
    data_combined = combine_cognition_data()
    data_trial = create_trial_data(data_combined)
    data_et = create_et_data(data_combined)
    data_subject = create_data_subject(data_combined)
    create_data_prolific(data_subject)
    summarize_datasets(data_et, data_trial, data_subject)
