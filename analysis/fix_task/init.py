import os

import pandas as pd

from analysis.fix_task.calibration import analyze_calibration
from analysis.fix_task.correlations import corr_analysis
from analysis.fix_task.data_quality import grand_mean_offset, outcome_over_trials
from analysis.fix_task.gaze_saccade import check_gaze_saccade
from analysis.fix_task.main_effects import main_effect
from analysis.fix_task.positions import compare_positions
from analysis.fix_task.randomization import check_randomization
from analysis.fix_task.visualize_gaze import visualize_exemplary_run, fix_heatmap
from utils.data_frames import merge_by_index
from utils.plots import get_box_plots
from utils.tables import summarize_datasets


def analyze_fix_task():

    print('################################### \n'
          'Analyze fix task data \n'
          '################################### \n')

    data_et = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_et.csv'))
    data_et_fix = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_et_fix.csv'))
    data_trial_fix = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_trial_fix.csv'))
    data_trial = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join('data', 'fix_task', 'added_var', 'data_subject.csv'))

    print('Datasets read from data/fix_task/added_var (all trials): ')
    summarize_datasets(data_et, data_trial, data_subject)

    print('Datasets read from data/fix_task/added_var (fix trials): ')
    summarize_datasets(data_et_fix, data_trial_fix, data_subject)

    # Design checks
    check_randomization(data_trial_fix)
    check_gaze_saccade(data_et, data_trial)

    # Descriptives (not necessary)
    # compare_conditions_subject(data_subject, data_trial_fix, 'offset')
    # compare_conditions_subject(data_subject, data_trial_fix, 'precision')

    main_effect(data_trial_fix, data_subject)
    outcome_over_trials(data_trial_fix, 'precision')
    compare_positions(data_trial_fix, 'precision')

    # Categorical confounders analysis
    for outcome in ['offset', 'precision', 'fps']:
        get_box_plots(data_subject, outcome, [
            'vertPosition', 'gender', 'ethnic',
            'degree', 'browser', 'glasses', 'sight', 'sight'],
                      ('box_plots_confounders_vs_' + outcome),
                      'results', 'plots', 'fix_task')

    # Correlations
    corr_analysis(data_trial_fix, data_subject)

    # Additional
    analyze_calibration(data_et, data_trial)
    data_trial_fix = grand_mean_offset(data_et_fix, data_trial_fix)

    # Visualize_exemplary_run
    data_plot = merge_by_index(data_et_fix, data_trial_fix, 'chin')
    visualize_exemplary_run(data_plot.loc[
        (data_plot['run_id'] == 43) & (data_plot['chin'] == 0), :])

    # Heatmap for all gaze points
    fix_heatmap(data_et_fix)
