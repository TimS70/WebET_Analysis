import os

import matplotlib.pyplot as plt
import pandas as pd

from data_prep.add_variables.data_quality.offset import add_offset
from data_prep.add_variables.data_quality.precision import \
    distance_from_xy_mean_square, aggregate_precision_from_et_data
from utils.combine import merge_by_index
from visualize.all_tasks import spaghetti_plot, save_plot


# Median offset across calibration trials
# Does data quality improve during calibration?


def analyze_calibration():

    print(
        """
            ###############################
            Analyze calibration
            ###############################
        """
    )

    data_et = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_et.csv'))

    data_trial = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_trial.csv'))

    data_et = add_offset(data_et)
    grouped = data_et \
        .groupby(['run_id', 'trial_index'], as_index=False) \
        .agg(offset=('offset', 'mean')) \
        .agg(offset_px=('offset_px', 'mean'))

    data_trial = merge_by_index(data_trial, grouped, 'offset', 'offset_px')
    data_et = distance_from_xy_mean_square(data_et)
    data_trial = aggregate_precision_from_et_data(data_trial, data_et)

    data_et_calibration = data_et[
        data_et['trial_type'] == 'eyetracking-calibration']
    data_trial_calibration = data_trial[
        data_trial['trial_type'] == 'eyetracking-calibration']

    # Add median offset
    grouped = data_et_calibration \
        .groupby(['run_id', 'trial_index'])['offset'].median() \
        .reset_index() \
        .rename(columns={'offset': 'offset_median'})
    data_trial_calibration = data_trial_calibration.merge(
        grouped,
        on=['run_id', 'trial_index'],
        how='left'
    )

    plot_outcome_vs_trials(data_trial_calibration, 'offset_median', 103)
    plot_outcome_vs_trials(data_trial_calibration, 'precision', 103)


def plot_outcome_vs_trials(data_trial_calibration, outcome, run):
    spaghetti_plot(
        data_trial_calibration.loc[(
            (data_trial_calibration['chinFirst'] == 0) &
            (data_trial_calibration['chin'] == 0)
        ) | (
            (data_trial_calibration['chinFirst'] == 1) &
            (data_trial_calibration['chin'] == 1)
        ), :],
        'withinTaskIndex', outcome, run)

    plt.ylim(0, 1)
    plt.title((outcome + ' across calibration for chin==0'),
              loc='center', fontsize=12, fontweight=0, color='grey')
    plt.xlabel('withinTaskIndex')
    plt.ylabel(outcome)

    save_plot(file_name='calibration_' + outcome + '_vs_trials.png',
              path=os.path.join('results', 'plots', 'fix_task'))
    plt.close()
