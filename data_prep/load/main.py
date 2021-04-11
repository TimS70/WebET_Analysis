from data_prep.load.eye_tracking import create_et_data_2, create_et_data
from data_prep.load.cognition import combine_cognition_data
from data_prep.load.subject import create_data_subject
from data_prep.load.trial import create_trial_data
from utils.save_data import save_all_three_datasets


def create_datasets_from_cognition(path_origin, path_target):
    data_combined = combine_cognition_data(path_origin)
    data_trial = create_trial_data(data_combined)
    data_et = create_et_data(data_combined, n_bins=10)
    # Alternative method
    # data_et = create_et_data_2(data_combined)

    data_subject = create_data_subject(data_combined)

    save_all_three_datasets(
        data_et, data_trial, data_subject, path_target)
