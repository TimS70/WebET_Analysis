import os

from analysis.fix_task.chin_rest import test_chin_rest
from analysis.fix_task.correlations import corr_analysis
from analysis.fix_task.data_quality import outcome_over_trials_vs_chin, \
    outcome_over_trials
from analysis.fix_task.glasses import test_glasses
from analysis.fix_task.positions import compare_positions
from analysis.fix_task.randomization import check_randomization
from data_prep.cleaning.corr_data import clean_corr_data
from utils.combine_frames import merge_by_index
from utils.save_data import load_all_three_datasets
from visualize.all_tasks import corr_matrix, corr_plot_split
from visualize.all_tasks import get_box_plots
from visualize.choice import plot_example_eye_movement, \
    plot_categorical_confounders
from visualize.fix_task.main import visualize_exemplary_run, fix_heatmap, \
    hist_plots_quality
from visualize.fix_task.positions import plot_top_vs_bottom_positions


def analyze_choice_task():
    print('################################### \n'
          'Analyze choice data \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'choice_task', 'cleaned'))

    plot_categorical_confounders(data_subject)
    plot_example_eye_movement(data_et, data_trial,
                              data_subject['run_id'].unique()[0])

    # corr_analysis_subject
    data_plot = clean_corr_data(
        data_subject[[
            'run_id', 'choseLL', 'choice_rt',
            'chinFirst', 'LL_top', 'logK',
            'attributeIndex', 'optionIndex', 'payneIndex', 'fps',
            'gender', 'degree', 'age']])

    corr_columns = [
        'age', 'choseLL',
        'attributeIndex', 'optionIndex', 'payneIndex',
        'choice_rt']

    corr_plot_split(data_plot, corr_columns,
                    'corr_vars_vs_chinFirst_trial.png', 'chinFirst',
                    'results', 'plots', 'choice_task', 'correlations')

    corr_columns = [
        'choseLL', 'choice_rt',
        'chinFirst', 'LL_top', 'logK',
        'attributeIndex', 'optionIndex', 'payneIndex', 'fps', 'age']

    corr_matrix(data_plot, corr_columns,
                'table_p', 'subject_corr_p.csv',
                'results', 'tables', 'choice_task', 'correlations')
    corr_matrix(data_plot, corr_columns,
                'table_n', 'subject_corr_n.csv',
                'results', 'tables', 'choice_task', 'correlations')
    corr_matrix(data_plot, corr_columns,
                'heatmap', 'subject_corr_heatmap.png',
                'results', 'plots', 'choice_task', 'correlations')

    # corr_analysis trial
    data_plot = clean_corr_data(
        data_trial.loc[:, [
                              'run_id', 'chinFirst', 'withinTaskIndex',
                              'choseLL', 'k',
                              'attributeIndex', 'optionIndex', 'payneIndex',
                              'trial_duration_exact']])

    corr_columns = [
        'choseLL', 'k', 'attributeIndex',
        'optionIndex', 'payneIndex', 'trial_duration_exact']

    corr_plot_split(data_plot, corr_columns,
                    'corr_vars_vs_chinFirst_trial.png', 'chinFirst',
                    'results', 'plots', 'choice_task', 'correlations')

    corr_columns = [
        'chinFirst', 'withinTaskIndex', 'choseLL', 'k', 'attributeIndex',
        'optionIndex', 'payneIndex', 'trial_duration_exact']

    corr_matrix(data_plot, corr_columns,
                'table_p', 'trial_corr_p.csv',
                'results', 'tables', 'choice_task', 'correlations')
    corr_matrix(data_plot, corr_columns,
                'table_n', 'trial_corr_n.csv',
                'results', 'tables', 'choice_task', 'correlations')
    corr_matrix(data_plot, corr_columns,
                'heatmap', 'trial_corr_heatmap.png',
                'results', 'plots', 'choice_task', 'correlations')


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

    test_chin_rest(data_trial, data_subject)
    test_glasses(data_trial, data_subject)

    outcome_over_trials_vs_chin(data_trial, 'offset')
    compare_positions(data_trial, 'offset')
    plot_top_vs_bottom_positions(data_trial, 'offset')

    outcome_over_trials_vs_chin(data_trial, 'precision')
    compare_positions(data_trial, 'precision')
    plot_top_vs_bottom_positions(data_trial, 'precision')

    outcome_over_trials(data_trial, 'offset')
    compare_positions(data_trial, 'offset')

    outcome_over_trials(data_trial, 'precision')
    compare_positions(data_trial, 'precision')

    # Categorical confounders analysis
    for outcome in ['offset', 'precision', 'fps']:
        get_box_plots(
            data_subject, outcome,
            ['vertPosition', 'gender', 'ethnic',
             'degree', 'browser', 'glasses', 'sight', 'sight'],
            ('box_plots_confounders_vs_' + outcome),
            'results', 'plots', 'fix_task', outcome)

    # Correlations
    corr_analysis(data_trial, data_subject)

    # Visualize_exemplary_run
    data_plot = merge_by_index(data_et, data_trial, 'chin')
    visualize_exemplary_run(data_plot.loc[
                            (data_plot['run_id'] == 43) & (
                                        data_plot['chin'] == 0), :])

    # Heatmap for all gaze points
    fix_heatmap(data_et)
