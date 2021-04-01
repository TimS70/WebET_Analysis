import os

import pandas as pd

from analysis.choice_task.test_clusters import test_transition_clusters
from data_prep.add_variables.both_tasks.subject import add_fps_subject_level, \
    add_max_trials, \
    add_glasses_binary, add_recorded_date, add_window
from data_prep.add_variables.both_tasks.trial import add_fps_trial_level, \
    add_window_size, \
    add_exact_trial_duration, add_new_task_nr, add_trial_type_new, \
    add_fix_task, add_within_task_index
from data_prep.add_variables.choice.aoi import create_aoi_columns, \
    match_remaining_et_trials, \
    add_aoi_counts_on_trial_level, add_fixation_counter, \
    count_fixations_on_trial_level, add_quadrant, add_aoi
from data_prep.add_variables.choice.behavior import choice_response_variables, \
    add_mean_choice_rt
from data_prep.add_variables.choice.choice_options import \
    identify_amount_left, add_choice_options_num, \
    reformat_attributes, add_k, top_bottom_attributes
from data_prep.add_variables.choice.et_indices import add_et_indices
from data_prep.add_variables.choice.eye_tracking import add_et_indices_subject
from utils.combine import merge_by_index, merge_by_subject
from utils.save_data import load_all_three_datasets, save_all_three_datasets, \
    write_csv
from visualize.eye_tracking import plot_et_scatter


def add_variables_global(path_origin, path_target):
    print('################################### \n'
          'Create global variables \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(path_origin)

    # Add Counts
    grouped = data_et\
        .groupby(['run_id', 'trial_index'], as_index=False) \
        .agg(x_count=('x', 'count'))
    data_trial = merge_by_index(data_trial, grouped, 'x_count')

    # Bug
    data_trial = add_window_size(data_trial)
    data_trial = add_exact_trial_duration(data_trial)
    data_trial = add_new_task_nr(data_trial)
    data_trial = add_trial_type_new(data_trial)
    data_trial = add_fix_task(data_trial)
    data_trial = add_within_task_index(data_trial)
    data_trial = add_fps_trial_level(data_trial)

    data_subject = add_fps_subject_level(data_subject, data_trial)
    data_subject = add_max_trials(data_subject, data_trial)
    data_subject = add_glasses_binary(data_subject)
    data_subject = add_recorded_date(data_subject, data_trial)
    data_subject = add_window(data_subject, data_trial)



    save_all_three_datasets(data_et, data_trial, data_subject, path_target)


def add_choice_behavioral_variables(path_origin, path_target, path_fix_subject):
    print('################################### \n'
          'Add variables for choice data \n'
          '################################### \n')

    data_trial = pd.read_csv(os.path.join(path_origin, 'data_trial.csv'))
    data_subject = pd.read_csv(os.path.join(path_origin, 'data_subject.csv'))

    summary = pd.DataFrame({
        'dataset': [
            'data_trial',
            'data_subject'],
        'prolific_ids': [
            len(data_trial['prolificID'].unique()),
            len(data_subject['prolificID'].unique())],
        'runs': [
            len(data_trial['run_id'].unique()),
            len(data_subject['run_id'].unique())],
        'n_trials': [
            len(data_trial),
            '-']})
    print(f"""{summary} \n""")

    # Add data from fixation task
    data_subject_fix = pd.read_csv(os.path.join(path_fix_subject,
                                                'data_subject.csv'))
    print(data_subject_fix.iloc[:, 23])
    print(data_subject_fix.iloc[:, 23].dtypes)
    data_subject = merge_by_subject(data_subject, data_subject_fix,
                                    'offset', 'precision', 'hit_ratio',
                                    'n_valid_dots')
    # Information attributes
    data_trial = identify_amount_left(data_trial)
    data_trial = add_choice_options_num(data_trial)
    data_trial = reformat_attributes(data_trial)
    data_trial = data_trial.assign(
        k=add_k(data_trial['aLL'], data_trial['aSS'], data_trial['tLL']))
    data_trial = top_bottom_attributes(data_trial)

    # Behavioral responses
    data_trial = choice_response_variables(data_trial)
    data_subject = add_mean_choice_rt(data_subject, data_trial)

    grouped = data_trial \
        .groupby(['run_id'], as_index=False) \
        .agg(choseLL=('choseLL', 'mean'),
             choseTop=('choseTop', 'mean'),
             LL_top=('LL_top', 'mean'))

    data_subject = merge_by_subject(data_subject, grouped,
                                    'choseLL', 'choseTop', 'LL_top')

    write_csv(data_trial, 'data_trial.csv', path_target)
    write_csv(data_subject, 'data_subject.csv', path_target)


def add_aoi_et(aoi_width, aoi_height, path_origin, path_target):
    data_et = pd.read_csv(os.path.join(path_origin, 'data_et.csv'))

    if (aoi_width >= 0.5) | (aoi_height >= 0.5):
        print(f"""Define the 4 quadrants of the screen """
              f"""as AOIs. \n""")
        data_et = add_quadrant(data_et)
        data_et['aoi'] = data_et['quadrant']

    else:
        print(f"""Added AOIs with width={aoi_width} and """
              f"""height={aoi_height} to """
              f"""n={len(data_et['run_id'].unique())} runs""")
        data_et = add_aoi(data_et, aoi_width, aoi_height)

    freq_table = pd.crosstab(index=data_et['aoi'],
                             columns="count")

    print(f"""Gaze points across AOIs: \n"""
          f"""{freq_table} \n""")

    write_csv(data_et, 'data_et.csv', path_target)

    return data_et


def add_choice_et_variables(min_required_trials, min_gaze_points,
                            path_origin, path_target):

    data_et, data_trial, data_subject = load_all_three_datasets(path_origin)

    data_et = merge_by_index(data_et, data_trial, 'amountLeft', 'LL_top')

    data_et = create_aoi_columns(data_et)
    data_trial = match_remaining_et_trials(data_trial, data_et)
    data_trial = add_aoi_counts_on_trial_level(data_trial, data_et)
    data_trial = add_et_indices(data_trial, data_et,
                                min_gaze_points=min_gaze_points)

    data_subject = add_et_indices_subject(
        data_subject, data_trial, min_required_trials=min_required_trials)

    data_et = add_fixation_counter(data_et)

    data_trial = count_fixations_on_trial_level(data_trial, data_et)
    data_trial = test_transition_clusters(data_trial)

    save_all_three_datasets(data_et, data_trial, data_subject, path_target)
