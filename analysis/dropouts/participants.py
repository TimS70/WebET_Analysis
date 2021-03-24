import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import MultiIndex

from analysis.dropouts.runs import multi_participation_by_run
from data_prep.cleaning.prolific_ids import drop_duplicate_ids
from utils.add_next_trial import add_next_trial
from utils.data_frames import merge_by_subject
from visualize.all_tasks import save_plot
from utils.tables import write_csv
from visualize.dropouts import plot_incomplete_runs


def dropouts_participants(data_subject, data_trial):

    # Mark participants with trials
    data_subject['status_2_id'] = np.nan
    data_subject.loc[
        ~data_subject['run_id'].isin(data_trial['run_id']),
        'status_2_id'] = 'no_trials'

    runs_returned_no_trials = data_subject.loc[
              (data_subject['status'] == 'RETURNED') &
              (data_subject['status_2_id'] == 'no_trials'),
              'prolificID'].unique()
    print(f"""Returned and no trials: {len(runs_returned_no_trials)}""")

    # Check for multiple attempts
    print('Attempts in total')
    attempts_by_id = multi_participation_by_run(data_trial)

    print('Attempts approved')
    ids_one_attempt, ids_multiple_attempts = multi_participation_by_run(
        data_trial[data_trial['status'] == 'APPROVED'])

    data_subject.loc[
        data_subject['prolificID'].isin(ids_one_attempt),
        'status_2_id'] = 'attempts_one'

    data_subject.loc[
        data_subject['prolificID'].isin(ids_multiple_attempts),
        'status_2_id'] = 'attempts_multiple'

    print('Attempts not approved')
    ids_one_attempt, ids_multiple_attempts = multi_participation_by_run(
        data_trial[data_trial['status'] != 'APPROVED'])

    data_subject.loc[
        data_subject['prolificID'].isin(ids_one_attempt),
        'status_2_id'] = 'attempts_one'

    data_subject.loc[
        data_subject['prolificID'].isin(ids_multiple_attempts),
        'status_2_id'] = 'attempts_multiple'

    # Conclusions
    freq_table_status = pd.crosstab(
              index=drop_duplicate_ids(data_subject)['status'],
              columns="n")
    print(f"""Freq_table status: {freq_table_status} \n""")

    grouped = data_subject \
        .assign(status_bin=(data_subject['status'] == 'APPROVED').astype(int)) \
        .groupby(['status', 'status_2_id'], as_index=False) \
        .agg(n=('prolificID', 'nunique'))
    print(f"""Grouped status: \n"""
          f"""{grouped} \n""")

    print(f"""Freq_table status_2_d: \n"""
          f"""{pd.crosstab(
              index=drop_duplicate_ids(data_subject)['status_2_id'], 
              columns="n")} \n""")

    grouped = data_subject \
        .assign(status_bin=(data_subject['status'] == 'APPROVED').astype(int)) \
        .groupby(['status_2_id', 'status'], as_index=False) \
        .agg(n=('prolificID', 'nunique'))
    print(f"""Grouped status: \n"""
          f"""{grouped} \n""")