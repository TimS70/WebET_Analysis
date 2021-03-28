import os

import pandas as pd

from analysis.choice_task.test_clusters import test_transition_clusters
from data_prep.add_variables.choice.aoi import create_aoi_columns, \
    match_remaining_et_trials, \
    add_aoi_counts_on_trial_level, add_fixation_counter, \
    count_fixations_on_trial_level, add_quadrant, add_aoi
from data_prep.add_variables.choice.behavior import choice_response_variables, add_mean_choice_rt
from data_prep.add_variables.choice.choice_options import identify_amount_left, add_choice_options_num, \
    reformat_attributes, \
    add_k, top_bottom_attributes
from data_prep.add_variables.choice.et_indices import add_et_indices
from data_prep.add_variables.choice.eye_tracking import add_et_indices_subject
from data_prep.add_variables.both_tasks.subject import add_fps_subject_level, add_max_trials, \
    add_glasses_binary, add_recorded_date, add_employment_status, add_full_time_binary
from data_prep.add_variables.both_tasks.trial import add_fps_trial_level, merge_count_by_index, add_window_size, \
    add_exact_trial_duration, add_new_task_nr, add_trial_type_new, add_fix_task, \
    add_within_task_index
from utils.combine_frames import merge_mean_by_subject, merge_by_index
from utils.save_data import load_all_three_datasets, save_all_three_datasets, \
    write_csv
from visualize.eye_tracking import plot_et_scatter


def add_variables_global():
    print('################################### \n'
          'Create global variables \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'all_trials', 'combined'))

    n_approved_unique = len(
        data_subject.loc[data_subject['status'] == 'APPROVED',
                         'prolificID'].unique())

    n_approved = len(data_subject.loc[
                     data_subject['status'] == 'APPROVED', :])

    print(f"""Number of approved runs: """
          f"""n={n_approved_unique} unique participants """
          f"""({n_approved} approved IDs, incl. duplicates). \n""")

    # data_et = invert_y_axis(data_et)
    # data_trial = invert_y_pos(data_trial)

    data_trial = merge_count_by_index(data_trial, data_et, 'x')

    # Bug
    # data_trial = add_position_index(data_trial)
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
    data_subject = add_employment_status(data_subject)
    data_subject = add_full_time_binary(data_subject)

    save_all_three_datasets(
        data_et, data_trial, data_subject,
        os.path.join('data', 'all_trials', 'added_var'))


def add_choice_behavioral_variables():
    print('################################### \n'
          'Add variables for choice data \n'
          '################################### \n')

    data_trial = pd.read_csv(os.path.join(
        'data', 'choice_task', 'raw',
        'data_trial.csv'))

    data_subject = pd.read_csv(os.path.join(
        'data', 'choice_task', 'raw',
        'data_subject.csv'))

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
    data_subject_fix = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var',
                     'data_subject.csv'))
    data_subject = merge_mean_by_subject(
        data_subject, data_subject_fix,
        'offset', 'precision', 'hit_ratio', 'n_valid_dots')

    # Information attributes
    data_trial = identify_amount_left(data_trial)
    data_trial = add_choice_options_num(data_trial)
    data_trial = reformat_attributes(data_trial)
    data_trial = data_trial.assign(
        k=add_k(data_trial['aLL'], data_trial['aSS'],
                data_trial['tLL']))
    data_trial = top_bottom_attributes(data_trial)

    # Behavioral responses
    data_trial = choice_response_variables(data_trial)

    data_subject = add_mean_choice_rt(
        data_subject, data_trial)

    data_subject = merge_mean_by_subject(
        data_subject, data_trial,
        'choseLL', 'choseTop', 'LL_top')

    write_csv(data_trial,
              'data_trial.csv',
              'data', 'choice_task', 'added_var')

    write_csv(data_subject,
              'data_subject.csv',
              'data', 'choice_task', 'added_var')


def add_aoi_et(aoi_width=0.3, aoi_height=0.3):

    data_et = pd.read_csv(os.path.join(
        'data', 'choice_task', 'raw', 'data_et.csv'))

    if (aoi_width >= 0.5) | (aoi_height >= 0.5):
        print(f"""Define the 4 quadrants of the screen """
              f"""as AOIs. \n""")
        data_et = add_quadrant(data_et)
        data_et['aoi'] = data_et['quadrant']

    else:
        print(f"""AOIs with width={aoi_width} and """
              f"""heigth={aoi_height}. \n""")
        data_et = add_aoi(data_et, aoi_width, aoi_height)

    freq_table = pd.crosstab(
        index=data_et['aoi'],
        columns="count")

    print(
        f"""Gaze points across AOIs: \n"""
        f"""{freq_table} \n""")

    plot_et_scatter(
        x=data_et['x'], y=data_et['y'],
        title='AOI raw for all runs ',
        file_name='aoi_scatter.png',
        path=os.path.join('results', 'plots', 'choice_task',
                          'et'))

    print(f"""Added AOIs to """
          f"""{len(data_et['run_id'].unique())} """
          f"""runs \n""")

    write_csv(data_et, 'data_et.csv',
              os.path.join('data', 'choice_task',
                           'added_var'))

    return data_et


def add_choice_et_variables(min_required_trials,
                            min_gaze_points):

    data_et, data_trial, data_subject = \
        load_all_three_datasets(
        os.path.join('data', 'choice_task', 'added_var'))

    data_et = create_aoi_columns(data_et)
    data_trial = match_remaining_et_trials(
        data_trial, data_et)
    data_trial = add_aoi_counts_on_trial_level(
        data_trial, data_et)
    data_trial = add_et_indices(
        data_trial, data_et,
        min_gaze_points=min_gaze_points)

    data_subject = add_et_indices_subject(
        data_subject, data_trial,
        min_required_trials=min_required_trials)

    data_et = add_fixation_counter(data_et)

    data_trial = count_fixations_on_trial_level(
        data_trial, data_et)
    data_trial = test_transition_clusters(data_trial)

    save_all_three_datasets(
        data_et, data_trial, data_subject,
        os.path.join('data', 'choice_task', 'added_var'))
