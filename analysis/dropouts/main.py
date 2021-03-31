import os

import pandas as pd

from analysis.dropouts.participants import dropouts_participants
from analysis.dropouts.runs import report_incomplete_runs, dropout_by_task_nr, dropout_by_type, check_calibration, \
    multi_participation_by_type, check_et_initialization
from utils.combine import merge_by_subject


def analyze_dropouts(path_origin):
    print('################################### \n'
          'Analyze dropouts \n'
          '################################### \n')

    data_subject = pd.read_csv(os.path.join(path_origin, 'data_subject.csv'))
    data_trial = pd.read_csv(os.path.join(path_origin, 'data_trial.csv'))

    data_trial = merge_by_subject(data_trial, data_subject,
                                  'prolificID', 'status')

    # Filter those from prolific
    data_subject = data_subject[pd.notna(data_subject['prolificID'])]
    data_trial = data_trial[data_trial['run_id'].isin(data_subject['run_id'])]

    dropouts_participants(data_subject, data_trial)

    # Check incomplete runs
    report_incomplete_runs(data_trial)
    dropout_by_task_nr(data_trial)
    dropout_by_type(data_trial)
    check_calibration(data_trial)
    multi_participation_by_type(data_trial)
    check_et_initialization(data_subject, data_trial)