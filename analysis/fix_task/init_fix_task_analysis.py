import os

import pandas as pd

from analysis.fix_task.calibration import analyze_calibration
from analysis.fix_task.correlations import corr_analysis
from analysis.fix_task.data_quality import grand_mean_offset, outcome_over_trials_vs_chin, hist_plots_quality, \
    outcome_over_trials
from analysis.fix_task.gaze_saccade import check_gaze_saccade
from analysis.fix_task.main_effects import main_effect
from analysis.fix_task.positions import compare_positions
from analysis.fix_task.randomization import check_randomization
from analysis.fix_task.visualize_gaze import visualize_exemplary_run, fix_heatmap
from utils.data_frames import merge_by_index
from utils.plots import get_box_plots, save_plot
from utils.tables import summarize_datasets, load_all_three_datasets


def analyze_fix_task():

    print('################################### \n'
          'Analyze fix task data \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'fix_task', 'added_var'))

    describe_data_quality = data_subject.loc[:, [
                                                    'fps', 'offset',
                                                    'offset_px', 'precision',
                                                    'precision_px'
                                                ]].describe()
    print(f"""FPS: \n{describe_data_quality}""")

    hist_plots_quality(data_subject)

    # Design checks
    check_randomization(data_trial)
    # check_gaze_saccade()

    # Descriptives (not necessary)
    # compare_conditions_subject(data_subject, data_trial, 'offset')
    # compare_conditions_subject(data_subject, data_trial, 'precision')

    main_effect(data_trial, data_subject)

    outcome_over_trials_vs_chin(data_trial, 'offset')
    compare_positions(data_trial, 'offset')

    outcome_over_trials_vs_chin(data_trial, 'precision')
    compare_positions(data_trial, 'precision')

    outcome_over_trials(data_trial, 'offset')
    compare_positions(data_trial, 'offset')

    outcome_over_trials(data_trial, 'precision')
    compare_positions(data_trial, 'precision')

    # Categorical confounders analysis
    for outcome in ['offset', 'precision', 'fps']:
        get_box_plots(data_subject, outcome, [
            'vertPosition', 'gender', 'ethnic',
            'degree', 'browser', 'glasses', 'sight', 'sight'],
                      ('box_plots_confounders_vs_' + outcome),
                      'results', 'plots', 'fix_task')

    # Correlations
    corr_analysis(data_trial, data_subject)

    # Additional
    # analyze_calibration(data_et, data_trial)
    data_trial = grand_mean_offset(data_et, data_trial)

    # Visualize_exemplary_run
    data_plot = merge_by_index(data_et, data_trial, 'chin')
    visualize_exemplary_run(data_plot.loc[
        (data_plot['run_id'] == 43) & (data_plot['chin'] == 0), :])

    # Heatmap for all gaze points
    fix_heatmap(data_et)
