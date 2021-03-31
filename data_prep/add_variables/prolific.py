import os

import pandas as pd

from data_prep.add_variables.both_tasks.subject import add_employment_status, \
    add_full_time_binary
from utils.save_data import write_csv


def add_prolific_demographic_variables(path_origin, path_target):
    data_subject = pd.read_csv(os.path.join(path_origin, 'data_subject.csv'))
    data_subject = add_employment_status(data_subject)
    data_subject = add_full_time_binary(data_subject)
    write_csv(data_subject, 'data_subject.csv', path_target)
