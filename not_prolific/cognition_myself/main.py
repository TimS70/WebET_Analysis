import os

from data_prep.add_variables.main import add_variables_global
from data_prep.load.main import create_datasets_from_cognition


def prep_data_cognition_myself():
    # create_datasets_from_cognition(
    #     path_origin=os.path.join('data', 'cognition_myself', 'raw'),
    #     path_target=os.path.join('data', 'cognition_myself', 'combined'))

    add_variables_global(
        path_origin=os.path.join('data', 'cognition_myself', 'combined'),
        path_target=os.path.join('data', 'cognition_myself', 'added_var'))
