import os

import numpy as np
import pandas as pd

from data_prep.cleaning.drop_invalid_data.et_data import drop_na_data_et
from data_prep.cleaning.drop_invalid_data.prolific_ids import drop_duplicate_ids
from data_prep.cleaning.drop_invalid_data.runs import clean_runs, \
    filter_approved_runs, match_runs
from data_prep.cleaning.find_invalid_runs.both_tasks import filter_runs_low_fps, \
    filter_runs_no_instruction, filter_full_but_no_et_data, filter_wrong_glasses
from data_prep.cleaning.find_invalid_runs.fix import \
    runs_with_incomplete_fix_tasks, filter_runs_bad_time_measure
from data_prep.cleaning.replace import clean_subject_variables
from utils.combine import combine_runs
from utils.save_data import summarize_datasets, save_all_three_datasets, \
    load_all_three_datasets, write_csv


def clean_global_data(path_origin, path_target=None,
                      prolific=False, approved=False, one_attempt=False,
                      max_t_task=None, min_fps=None,
                      additionally_bad_runs=None, exclude_runs_reason=None,
                      max_missing_et=None,
                      full_runs=False, valid_sight=False,
                      follow_instruction=False, correct_webgazer_clock=False,
                      complete_fix_task=False,
                      approval_rate=None):
    print('################################### \n'
          'Clean global datasets \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(path_origin)

    data_et = drop_na_data_et(data_et)

    if prolific:
        # Filter Prolific data
        runs_not_prolific = data_subject.loc[
            pd.isna(data_subject['prolificID']), 'run_id']

        print(f"""Filtering Prolific Data: \n"""
              f"""n={len(runs_not_prolific)} runs do not have a Prolific ID """
              f"""(e.g. from task development instead) and will be """
              f"""removed: \n""")

        data_et = clean_runs(data_et, runs_not_prolific, 'data_et')
        data_trial = clean_runs(data_trial, runs_not_prolific, 'data_trial')
        data_subject = clean_runs(data_subject, runs_not_prolific,
                                  'data_subject')

    if approved:
        data_subject, data_trial, data_et = filter_approved_runs(
            data_subject, data_trial, data_et)

    if one_attempt:
        # Clean multi-attempts
        print('Clean for multiple attempts: ')
        data_subject = drop_duplicate_ids(data_subject)
        data_trial = data_trial[
            data_trial['run_id'].isin(data_subject['run_id'])]
        data_et = data_et[
            data_et['run_id'].isin(data_subject['run_id'])]
        summarize_datasets(data_et, data_trial, data_subject)

        print('Match runs: ')

    data_subject, data_trial, data_et, n_missing_trial, n_missing_et = \
        match_runs(data_subject, data_trial, data_et)

    invalid_runs = []
    n_runs = len(data_trial['run_id'].unique())
    summary = []

    if full_runs:
        # Not enough trials
        runs_full_trial = data_trial.loc[
            data_trial['trial_type_new'] == 'end', 'run_id'].unique()

        runs_not_full_trial = np.setdiff1d(data_trial['run_id'].unique(),
                                           runs_full_trial)

        invalid_runs = combine_runs(invalid_runs, runs_not_full_trial)

        summary.append(['incomplete',
                        len(runs_not_full_trial) + n_missing_trial,
                        (len(runs_not_full_trial) + n_missing_trial) / n_runs])

    if max_missing_et is not None:
        runs_full_but_not_enough_et = filter_full_but_no_et_data(
            data_et, data_trial, max_missing_et)
        invalid_runs = combine_runs(invalid_runs, runs_full_but_not_enough_et)
        summary.append(
            ['runs_not_enough_et',
             len(runs_full_but_not_enough_et) + n_missing_et,
             (len(runs_full_but_not_enough_et) + n_missing_et) / n_runs])

    if complete_fix_task:
        # Fixation task. No validation possible
        data_trial_fix = data_trial[
            (data_trial['trial_type'] == 'eyetracking-fix-object') &
            (data_trial['trial_duration'] == 5000)]

        runs_incomplete_fix_task = runs_with_incomplete_fix_tasks(
            data_trial_fix)

        invalid_runs = combine_runs(invalid_runs, runs_incomplete_fix_task)
        summary.append(['runs_incomplete_fix_task',
                        len(runs_incomplete_fix_task),
                        len(runs_incomplete_fix_task) / n_runs])

    if correct_webgazer_clock:
        # Fixation task. No validation possible
        data_trial_fix = data_trial[
            (data_trial['trial_type'] == 'eyetracking-fix-object') &
            (data_trial['trial_duration'] == 5000)]

        runs_bad_time_measure = filter_runs_bad_time_measure(
            data_trial_fix, max_t_task=max_t_task)
        invalid_runs = combine_runs(invalid_runs, runs_bad_time_measure)
        summary.append(['runs_bad_time_measure',
                        len(runs_bad_time_measure),
                        len(runs_bad_time_measure) / n_runs])

    if follow_instruction:
        runs_not_follow_instructions = filter_runs_no_instruction(data_subject)
        invalid_runs = combine_runs(invalid_runs, runs_not_follow_instructions)
        summary.append(['runs_not_follow_instructions',
                        len(runs_not_follow_instructions),
                        len(runs_not_follow_instructions) / n_runs])

    if valid_sight:
        runs_cannot_see = filter_wrong_glasses(data_subject)
        invalid_runs = combine_runs(invalid_runs, runs_cannot_see)
        summary.append(['runs_cannot_see',
                        len(runs_cannot_see),
                        len(runs_cannot_see) / n_runs])

    if approval_rate is not None:
        print(data_subject[['num_approvals', 'num_rejections', 'prolific_score']])
        data_subject['approval_rate'] = \
            data_subject['num_approvals'] / (data_subject['num_approvals'] +
                                             data_subject['num_rejections'])
        approval_summary = data_subject[[
            'num_approvals', 'num_rejections', 'approval_rate',
            'prolific_score']].describe()

        print(f"""Approval rate and Prolific Score: \n"""
              f"""{approval_summary} \n""")

    if min_fps is not None:
        runs_low_fps = filter_runs_low_fps(data_trial, data_et, min_fps)
        invalid_runs = combine_runs(invalid_runs, runs_low_fps)
        summary.append(['runs_low_fps',
                        len(runs_low_fps),
                        len(runs_low_fps) / n_runs])

    if additionally_bad_runs is not None:
        runs_excluded = np.intersect1d(
            data_subject['run_id'].unique(), additionally_bad_runs)
        invalid_runs = combine_runs(invalid_runs, runs_excluded)
        summary.append([exclude_runs_reason,
                        len(runs_excluded),
                        len(runs_excluded) / n_runs])

    summary.append(['total',
                    len(invalid_runs),
                    len(invalid_runs) / n_runs])

    summary = pd.DataFrame(summary, columns=['name', 'n', 'percent']) \
        .sort_values(by='n')
    summary['percent'] = 100 * round(summary['percent'], 4)


    print(f"""\nIn total, n={len(invalid_runs)} have to be """
          f"""removed from n={n_runs} runs: \n"""
          f"""{summary} \n""")

    write_csv(data=summary,
              file_name='global_cleaning.csv',
              index=False,
              path=os.path.join('results', 'tables'))

    data_et = clean_runs(data_et, invalid_runs, 'data_et')
    data_trial = clean_runs(data_trial, invalid_runs, 'data_trial')
    data_subject = clean_runs(data_subject, invalid_runs, 'data_subject')

    if path_target is not None:
        save_all_three_datasets(data_et, data_trial, data_subject, path_target)

    return data_et, data_trial, data_subject