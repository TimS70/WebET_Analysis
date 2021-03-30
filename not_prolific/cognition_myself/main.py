import os

from data_prep.add_variables.main import add_variables_global
from data_prep.cleaning.all_trials import clean_global_data
from data_prep.load.main import create_datasets_from_cognition


def prep_data_cognition_myself():
    # create_datasets_from_cognition(
    #     path_origin=os.path.join('data', 'cognition_myself', 'raw'),
    #     path_target=os.path.join('data', 'cognition_myself', 'combined'))

    # add_variables_global(
    #     path_origin=os.path.join('data', 'cognition_myself', 'combined'),
    #     path_target=os.path.join('data', 'cognition_myself', 'added_var'))

    clean_global_data(
        path_origin=os.path.join('data', 'cognition_myself', 'added_var'),
        path_target=os.path.join('data', 'cognition_myself', 'cleaned'),
        prolific=False, approved=False, one_attempt=False,
        max_t_task=5500, min_fps=3,
        exclude_runs=None, exclude_runs_reason=None,
        max_missing_et=10,
        full_runs=True, valid_sight=True,
        follow_instruction=True, correct_webgazer_clock=True,
        complete_fix_task=True)
