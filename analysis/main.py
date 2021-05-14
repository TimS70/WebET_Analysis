import os

from statsmodels.stats.multicomp import pairwise_tukeyhsd

from analysis.fix_task.chin_rest import test_chin_rest
from analysis.fix_task.correlations import corr_analysis_fix
from analysis.fix_task.glasses import test_glasses
from analysis.fix_task.positions import compare_positions
from analysis.fix_task.randomization import check_randomization
from inference.F import anova_outcomes_factor
from inference.t_test import t_test_outcomes_vs_factor
from utils.combine import merge_by_index
from utils.save_data import load_all_three_datasets, write_csv
from visualize.all_tasks import get_box_plots
from visualize.fix_task.main import visualize_exemplary_run, fix_heatmaps, \
    hist_plots_quality, plot_outcome_over_trials, \
    plot_outcome_over_trials_vs_chin
from visualize.fix_task.positions import plot_top_vs_bottom_positions
from tqdm import tqdm


def analyze_fix_task(path_origin, path_plots, path_tables):
    data_et, data_trial, data_subject = load_all_three_datasets(path_origin)

    descriptives = round(data_subject[['offset', 'offset_px',
                                       'precision', 'precision_px',
                                       'fps', 'hit_ratio']].describe(), 4)

    # write_csv(data=descriptives, file_name='descriptives.csv',
    #           path=path_tables, index=True)
    #
    # print(f"""Describe data quality: \n"""
    #       f"""{descriptives} \n""")
    #
    # # Task order and position is analyzed in MLA
    #
    # data_subject['makeup'] = 0
    # data_subject.loc[(data_subject['eyeshadow'] == 1) |
    #                  (data_subject['masquara'] == 1) |
    #                  (data_subject['eyeliner'] == 1) |
    #                  (data_subject['browliner'] == 1), 'makeup'] = 1
    #
    # t_test_outcomes_vs_factor(data=data_subject,
    #                           factor='makeup',
    #                           dependent=False,
    #                           outcomes=['offset', 'precision'],
    #                           file_name='t_test_makeup_vs_outcomes.csv',
    #                           path=path_tables)
    #
    #
    # check_randomization(data_trial=data_trial,
    #                     path_plots=path_plots,
    #                     path_tables=path_tables)
    #
    # corr_analysis_fix(data_trial=data_trial, data_subject=data_subject,
    #                   path_plots=path_plots, path_tables=path_tables)
    #
    # # t-test for glasses vs. age
    # t_test_outcomes_vs_factor(data=data_subject,
    #                           factor='glasses_binary',
    #                           dependent=False,
    #                           outcomes=['age'],
    #                           file_name='t_test_glasses_vs_age.csv',
    #                           path=path_tables)
    #
    # test_chin_rest(data_trial=data_trial,
    #                data_subject=data_subject,
    #                path_plots=os.path.join(path_plots, 'chin_rest'),
    #                path_tables=os.path.join(path_tables, 'chin_rest'))
    # test_glasses(data_trial=data_trial,
    #              data_subject=data_subject,
    #              path_plots=os.path.join(path_plots, 'glasses'),
    #              path_tables=os.path.join(path_tables, 'glasses'))
    #
    # # Over the trials
    # for outcome in ['offset', 'precision']:
    #     plot_outcome_over_trials(
    #         data_trial[data_trial['fixTask'] == 1], outcome, path_plots)
    #     plot_outcome_over_trials_vs_chin(data_trial, outcome, path_plots)
    #     compare_positions(data_trial, outcome, path_tables)
    #     plot_top_vs_bottom_positions(data_trial, outcome, path_plots)
    #
    # # Categorical confounders analysis
    # for outcome in ['offset', 'precision', 'fps']:
    #     get_box_plots(
    #         data=data_subject,
    #         outcome=outcome,
    #         predictors=['vertPosition', 'gender', 'ethnic',
    #                     'degree', 'browser', 'glasses', 'sight', 'sight'],
    #         file_name='box_plots_confounders_vs_' + outcome + '.png',
    #         path_target=os.path.join(path_plots, outcome))
    #
    # for predictor in ['vertPosition', 'gender', 'ethnic',
    #                  'degree', 'browser', 'glasses', 'sight', 'makeup']:
    #     anova_outcomes_factor(data=data_subject,
    #                           factor=predictor,
    #                           outcomes=['offset', 'precision', 'fps'],
    #                           path=os.path.join(path_tables, 'confounders'))
    #
    # print('Test vertical position')
    # tukey = pairwise_tukeyhsd(endog=data_subject['fps'],
    #                           groups=data_subject['vertPosition'],
    #                           alpha=0.05)
    # print(tukey)
    #
    # tukey = pairwise_tukeyhsd(endog=data_subject['offset'],
    #                           groups=data_subject['browser'],
    #                           alpha=0.05)
    # print(tukey)
    #
    # Visualize_exemplary_run
    data_plot = merge_by_index(data_et, data_trial, 'chin')

    runs_glasses = data_subject.loc[
        data_subject['glasses_binary'] == 1,
        'run_id'].unique()

    for run in runs_glasses:
        visualize_exemplary_run(
            data=data_plot[
                (data_plot['run_id'] == run) &
                (data_plot['chin'] == 0)],
            path_target=os.path.join(path_plots, 'exemplary_runs', 'glasses_0',
                                     'no_chin'))

        visualize_exemplary_run(
            data=data_plot[
                (data_plot['run_id'] == run) &
                (data_plot['chin'] == 1)],
            path_target=os.path.join(path_plots, 'exemplary_runs', 'glasses_0',
                                     'chin'))

    runs_no_glasses = data_subject.loc[
        data_subject['glasses_binary'] == 0,
        'run_id'].unique()

    for run in runs_no_glasses:
        visualize_exemplary_run(
            data=data_plot[
                (data_plot['run_id'] == run) &
                (data_plot['chin'] == 0)],
            path_target=os.path.join(path_plots, 'exemplary_runs', 'glasses_1',
                                     'no_chin'))

        visualize_exemplary_run(
            data=data_plot[
                (data_plot['run_id'] == run) &
                (data_plot['chin'] == 1)],
            path_target=os.path.join(path_plots, 'exemplary_runs', 'glasses_1',
                                     'chin'))

    outlier_runs = data_subject.loc[
        (data_subject['glasses_binary'] == 0) &
        (data_subject['offset'] > 0.5),
        'run_id'].unique()

    for run in outlier_runs:

        visualize_exemplary_run(
            data=data_plot[
                (data_plot['run_id'] == run) &
                (data_plot['chin'] == 0)],
            path_target=os.path.join(path_plots, 'exemplary_runs', 'glasses_0',
                                     'outliers'))

    # Heatmap for all gaze points
    # fix_heatmaps(data=data_et,
    #              file_name='all.png',
    #              title='Heatmap of gaze points during the fixation task',
    #              path_target=os.path.join(path_plots, 'heatmaps'))

    # Heatmap for individual runs
    # for run in tqdm(data_et['run_id'].unique(),
    #                 desc='Plot fix task heatmaps: '):
    #
    #     fix_heatmaps(data=data_et[data_et['run_id'] == run],
    #                  title='Fix task heatmap for run #' + str(round(run)),
    #                  file_name=str(round(run)) + '.png',
    #                  path_target=os.path.join(path_plots, 'heatmaps'))
