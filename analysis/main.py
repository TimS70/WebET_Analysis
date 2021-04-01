import os

from analysis.fix_task.chin_rest import test_chin_rest
from analysis.fix_task.correlations import corr_analysis
from analysis.fix_task.data_quality import compare_conditions_subject
from analysis.fix_task.gaze_saccade import check_gaze_saccade
from analysis.fix_task.glasses import test_glasses
from analysis.fix_task.positions import compare_positions
from analysis.fix_task.randomization import check_randomization
from data_prep.cleaning.corr_data import clean_corr_data
from inference.F import anova_outcomes_factor
from inference.t_test import t_test_outcomes_vs_factor
from utils.combine import merge_by_index
from utils.save_data import load_all_three_datasets, write_csv
from visualize.all_tasks import save_plot
from visualize.all_tasks import get_box_plots
from visualize.choice import plot_example_eye_movement, \
    plot_categorical_confounders
from visualize.fix_task.main import visualize_exemplary_run, fix_heatmaps, \
    hist_plots_quality, plot_outcome_over_trials, \
    plot_outcome_over_trials_vs_chin
from visualize.fix_task.positions import plot_top_vs_bottom_positions
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.stats.anova import AnovaRM


def analyze_choice_task(path_origin, path_plots, path_tables):
    print('################################### \n'
          'Analyze choice data \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(path_origin)

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

    sns.set()
    sns.pairplot(data=data_plot,
                 vars=[...],
                 hue='chinFirst',
                 kind='reg',
                 corner=True,
                 plot_kws=dict(scatter_kws=dict(s=0.1)))
    save_plot(file_name='corr_vars_vs_chinFirst_trial.png',
              path=path_plots,
              message=True)
    plt.close()

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

    scatter_matrix(data_plot, corr_columns,
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


def analyze_fix_task(path_origin, path_plots, path_tables):

    data_et, data_trial, data_subject = load_all_three_datasets(path_origin)
    descriptives = round(data_subject[['offset', 'offset_px',
                                       'precision', 'precision_px',
                                       'fps', 'hit_ratio']].describe(), 4)

    write_csv(data_frame=descriptives, file_name='descriptives.csv',
              path=path_tables, index=True)

    print(f"""Describe data quality: \n"""
          f"""{descriptives} \n""")

    # Task order and position is analyzed in MLA

    data_subject['makeup'] = 0
    data_subject.loc[
        (data_subject['eyeshadow'] == 1) |
        (data_subject['masquara'] == 1) |
        (data_subject['eyeliner'] == 1) |
        (data_subject['browliner'] == 1), 'makeup'] = 1

    hist_plots_quality(data_subject, path_plots)

    check_randomization(data_trial, path_plots, path_tables)

    corr_analysis(data_trial, data_subject, path_plots, path_tables)
    exit()
    # t-test for glasses vs. age
    t_test_outcomes_vs_factor(data=data_subject,
                              factor='glasses_binary',
                              dependent=False,
                              outcomes=['age'],
                              file_name='t_test_glasses_vs_age.csv',
                              path=path_tables)

    test_chin_rest(data_trial=data_trial,
                   data_subject=data_subject,
                   path_plots=os.path.join(path_plots, 'chin_rest'),
                   path_tables=os.path.join(path_tables, 'chin_rest'))
    test_glasses(data_trial=data_trial,
                 data_subject=data_subject,
                 path_plots=os.path.join(path_plots, 'glasses'),
                 path_tables=os.path.join(path_tables, 'glasses'))

    # Over the trials
    for outcome in ['offset', 'precision']:
        plot_outcome_over_trials(data_trial, outcome, path_plots)
        plot_outcome_over_trials_vs_chin(data_trial, outcome, path_plots)
        compare_positions(data_trial, outcome, path_tables)
        plot_top_vs_bottom_positions(data_trial, outcome, path_plots)

    # Categorical confounders analysis
    for outcome in ['offset', 'precision', 'fps']:
        get_box_plots(
            data=data_subject,
            outcome=outcome,
            predictors=['vertPosition', 'gender', 'ethnic',
                        'degree', 'browser', 'glasses', 'sight', 'sight'],
            file_name='box_plots_confounders_vs_' + outcome + '.png',
            path_target=os.path.join(path_plots, outcome))

    for predictor in ['vertPosition', 'gender', 'ethnic',
                     'degree', 'browser', 'glasses', 'sight', 'makeup']:
        anova_outcomes_factor(data=data_subject,
                              factor=predictor,
                              path=os.path.join(path_tables, 'confounders'))

    print('Test vertical position')
    for outcome in ['offset', 'precision', 'fps']:
        print(outcome)
        tukey = pairwise_tukeyhsd(endog=data_subject[outcome],
                                  groups=data_subject['vertPosition'],
                                  alpha=0.05)
        print(tukey)

    # Visualize_exemplary_run
    # data_plot = merge_by_index(data_et, data_trial, 'chin')
    # visualize_exemplary_run(
    #     data=data_plot[
    #         (data_plot['run_id'] == data_plot['run_id'].unique()[0]) &
    #         (data_plot['chin'] == 0)],
    #     path_target=os.path.join(path_plots, 'exemplary_runs'))
    #
    # # Heatmap for all gaze points
    # fix_heatmaps(
    #     data=data_et,
    #     path_target=os.path.join(path_plots, 'fix_heatmaps'))
