import os
import subprocess

from amasino.cleaning import invalid_choice_runs
from amasino.prep_data_et import transform_xy_coordinates
from amasino.prep_data_trial import load_data, add_trial_index, \
    add_log_k, add_choseTop, add_choice_options
from analysis.choice_task.test_clusters import test_transition_clusters
from data_prep.add_variables.choice.aoi import match_remaining_et_trials, add_aoi_counts_on_trial_level, \
    add_fixation_counter, count_fixations_on_trial_level, create_aoi_columns
from data_prep.add_variables.choice.et_indices import add_et_indices
from data_prep.add_variables.main import add_aoi_et
from data_prep.cleaning.drop_invalid_data.runs import clean_runs
from utils.combine_frames import merge_by_index
from utils.save_data import save_all_three_datasets, load_all_three_datasets


def prep_data():
    data_et, data_trial = load_data()

    data_trial = add_trial_index(data_trial)
    data_trial['withinTaskindex'] = data_trial['trial_index']

    data_trial['trial_duration_exact'] = data_trial['rt']

    #For this, 1 = LL on top, Amt on left, 2 = SS on top, Amt on left,
    # 3 = LL on top, Time on left, and 4 = SS on top, Time on left
    data_trial['amountLeft'] = data_trial['LL_top'] \
        .replace([1, 2, 3, 4],
                 [1, 1, 0, 0])

    data_trial['LL_top'] = data_trial['LL_top'] \
        .replace([1, 2, 3, 4],
                 [1, 0, 1, 0])

    data_subject = data_trial \
        .groupby(['run_id'], as_index=False) \
        .agg(choseLL=('choseLL', 'mean'),
             rt=('rt', 'mean'),
             LL_top=('LL_top', 'mean'))

    data_trial = add_choice_options(data_trial)
    data_trial = add_choseTop(data_trial)

    # Eye-tracking Indices
    data_et['trial_index'] = data_et['withinTaskIndex']

    data_et = transform_xy_coordinates(data_et)
    data_et = add_aoi_et(data_et)
    data_et = merge_by_index(data_et, data_trial,
                             'amountLeft', 'LL_top',
                             'choseLL', 'choseTop')

    data_et = create_aoi_columns(data_et)

    data_trial = match_remaining_et_trials(data_trial, data_et)
    data_trial = add_aoi_counts_on_trial_level(data_trial, data_et)

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'amasino', 'added_var'))

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'amasino', 'added_var'))

    data_trial = add_et_indices(
        data_trial, data_et,
        min_gaze_points=3)

    data_et = add_fixation_counter(data_et)

    data_trial['withinTaskIndex'] = data_trial['trial_index']
    data_trial = count_fixations_on_trial_level(data_trial, data_et)
    data_trial = test_transition_clusters(data_trial)

    data_subject = add_log_k(data_subject, data_trial)

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'amasino', 'added_var'))


def clean_data():
    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'amasino', 'added_var'))

    # Cleaning
    invalid_runs = invalid_choice_runs(data_trial, data_et, data_subject)

    # Remove invalid runs
    data_subject = clean_runs(data_subject, invalid_runs, 'data_subject')
    data_trial = clean_runs(data_trial, invalid_runs, 'data_trial')
    data_et = clean_runs(data_et, invalid_runs, 'data_et')

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'amasino', 'cleaned'))

    return data_et, data_trial, data_subject


def analyze():
    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'amasino', 'added_var'))

    data_trial['trial_duration_exact'] = data_trial['rt']
    data_trial = add_choice_options(data_trial)

    # plot_example_eye_movement(data_et, data_trial,
    #                           data_subject['run_id'].unique()[0])
    # plot_choice_task_heatmap(data_et)

    subprocess.call(
        ['Rscript', '--vanilla', 'amasino/run_r_markdowns.R'],
        shell=True)


def test_amasino_data():
    prep_data()
    clean_data()
    # analyze()
