import os
import subprocess

import pandas as pd

from analysis.choice_task.correlations import corr_analysis_choice
from analysis.choice_task.test_clusters import add_transition_clusters
from analysis.demographics import analyze_demographics
from analysis.dropouts.main import analyze_dropouts
from analysis.fix_task.gaze_saccade import check_gaze_saccade
from analysis.fix_task.grand_mean_offset import grand_mean_offset
from analysis.main import analyze_fix_task
from data_prep.add_variables.data_quality.main import add_data_quality
from data_prep.add_variables.fit_k.call_from_py import add_log_k
from data_prep.add_variables.main import add_choice_behavioral_variables, \
    add_choice_et_variables, add_aoi_et, add_variables_global
from data_prep.add_variables.prolific import add_prolific_demographic_variables
from data_prep.cleaning.all_trials import clean_global_data
from data_prep.cleaning.fix_task import clean_data_fix
from data_prep.cleaning.choice import clean_data_choice
from data_prep.cleaning.replace import clean_subject_variables
from data_prep.clustering.main import init_cluster_correction
from data_prep.load.choice import load_choice_data
from data_prep.load.fix_task import load_fix_data
from data_prep.load.main import create_datasets_from_cognition
from data_prep.load.prolific import integrate_prolific_data
from inference.F import anova_outcomes_factor
from inference.t_test import t_test_outcomes_vs_factor
from not_prolific.amasino.main import test_amasino_data
from not_prolific.cognition_myself.main import \
    prep_and_analyze_data_cognition_myself
from utils.save_data import load_all_three_datasets, save_all_three_datasets, \
    write_csv
from visualize.all_tasks import get_box_plots, save_plot
from visualize.choice import plot_choice_task_heatmap, \
    plot_example_eye_movement, plot_log_k_frequency
from visualize.distributions import plot_histogram
from visualize.eye_tracking import plot_et_scatter

import matplotlib.pyplot as plt
import numpy as np

from visualize.fix_task.main import hist_plots_quality


def prep_global():
    add_variables_global(
        path_origin=os.path.join('data', 'all_trials', 'combined'),
        path_target=os.path.join('data', 'all_trials', 'added_var'))

    add_prolific_demographic_variables(
        path_origin=os.path.join('data', 'all_trials', 'added_var'),
        path_target=os.path.join('data', 'all_trials', 'added_var'))

    clean_subject_variables(
        path_origin=os.path.join('data', 'all_trials', 'added_var'),
        path_target=os.path.join('data', 'all_trials', 'added_var'))

    runs_no_saccade = [144, 171, 380]
    clean_global_data(
        path_origin=os.path.join('data', 'all_trials', 'added_var'),
        path_target=os.path.join('data', 'all_trials', 'cleaned'),
        prolific=True, approved=True, one_attempt=True,
        max_t_task=5500, min_fps=3,
        additionally_bad_runs=runs_no_saccade, exclude_runs_reason='No saccade',
        max_missing_et=10,
        full_runs=True, valid_sight=True,
        follow_instruction=True, correct_webgazer_clock=True,
        complete_fix_task=True,
        approval_rate=0.5)


def prep_fix():
    data_et, data_trial, data_subject = load_fix_data(
        path_origin=os.path.join('data', 'all_trials', 'cleaned'),
        path_target=os.path.join('data', 'fix_task', 'raw'))

    data_et, data_trial, data_subject = add_data_quality(
        max_offset=0.15,
        min_hits_per_dot=0.8,
        data_subject=data_subject,
        data_trial=data_trial,
        data_et=data_et)

    descriptives = round(data_subject[['offset', 'offset_px',
                                       'precision', 'precision_px',
                                       'fps', 'hit_ratio']].describe(), 4)

    print(f"""Describe data quality: \n"""
          f"""{descriptives} \n""")

    hist_plots_quality(data_subject,
                       path_plots=os.path.join('results', 'plots', 'fix_task'))

    outliers = data_subject.loc[
        (data_subject['offset'] > 0.5) |
        (data_subject['precision'] > 0.2),
        ['run_id', 'offset', 'precision', 'hit_mean', 'fps', 'glasses_binary']] \
        .T

    write_csv(data=outliers, file_name='outliers.csv',
              path=os.path.join('results', 'tables', 'fix_task'), index=True)

    print(f"""Outliers: {round(outliers, 4)}""")

    clean_data_fix(max_t_task=5500,
                   exclude_runs=[268, 325, 243, 425, 488,
                                 354, 293, 268  # Extreme offset
                                 ],
                   path_origin=os.path.join('data', 'fix_task', 'raw'),
                   path_target=os.path.join('data', 'fix_task', 'cleaned'))

    add_data_quality(max_offset=0.15,
                     min_hits_per_dot=0.8,
                     path_origin=os.path.join('data', 'fix_task', 'cleaned'),
                     path_target=os.path.join('data', 'fix_task', 'added_var'))


def prep_choice(main_aoi_width=0.4,
                main_aoi_height=0.4,
                correct_clusters=False,
                new_plots=True):
    # load_choice_data(path_origin=os.path.join('data', 'all_trials', 'cleaned'),
    #                  path_target=os.path.join('data', 'choice_task', 'raw'))
    #
    # add_choice_behavioral_variables(
    #     path_origin=os.path.join('data', 'choice_task', 'raw'),
    #     path_target=os.path.join('data', 'choice_task', 'added_var'),
    #     path_fix_subject=os.path.join('data', 'fix_task', 'added_var'))
    #
    # if new_plots:
    #     plot_choice_task_heatmap(
    #         path_origin=os.path.join('data', 'choice_task',
    #                                  'raw', 'data_et.csv'),
    #         path_target=os.path.join('results', 'plots',
    #                                  'choice_Task', 'individual_heatmaps', 'all'))
    #
    # add_aoi_et(aoi_width=main_aoi_width, aoi_height=main_aoi_height,
    #            path_origin=os.path.join('data', 'choice_task', 'raw'),
    #            path_target=os.path.join('data', 'choice_task', 'added_var'))
    #
    # if new_plots:
    #     data_plot = pd.read_csv(os.path.join(
    #         'data', 'choice_task', 'added_var', 'data_et.csv'))
    #     data_plot = data_plot[pd.notna(data_plot['aoi'])]
    #     plot_et_scatter(x=data_plot['x'], y=data_plot['y'],
    #                     title='AOI raw for all runs ',
    #                     file_name='aoi_scatter.png',
    #                     path=os.path.join('results', 'plots', 'choice_task', 'et'))
    #
    # if correct_clusters:
    #     data_et_corrected = init_cluster_correction(
    #         distance_threshold=0.25,
    #         min_cluster_size=50,
    #         min_ratio=0.5,
    #         max_deviation=0.25,
    #         aoi_width=main_aoi_width,
    #         aoi_height=main_aoi_height,
    #         message=False,
    #         path_origin=os.path.join('data', 'choice_task', 'added_var'),
    #         path_target=os.path.join('data', 'choice_task', 'added_var'))
    #
    #     plot_choice_task_heatmap(
    #         path_origin=os.path.join('data', 'choice_task',
    #                                  'raw', 'data_et.csv'),
    #         path_target=os.path.join('results', 'plots',
    #                                  'clustering', 'py_clusters',
    #                                  'heatmaps_selected'),
    #         runs=data_et_corrected['run_id'].unique())
    #
    # add_choice_et_variables(
    #     min_required_trials=5, min_gaze_points=3,
    #     path_origin=os.path.join('data', 'choice_task', 'added_var'),
    #     path_target=os.path.join('data', 'choice_task', 'added_var'))
    #
    # add_log_k(path=os.path.join('data', 'choice_task', 'added_var'),
    #           file_trial_input='data_trial.csv',
    #           file_subjects_to_merge='data_subject.csv')

    data_et, data_trial, data_subject = clean_data_choice(
        us_sample=False,
        min_hit_ratio=0.6,
        max_precision=None,  # 0.15,
        max_offset=None,  # 0.5,
        min_fps=5,
        min_rt=400, max_rt=10000,
        min_choice_percentage=0.01,
        max_choice_percentage=0.99,
        # exclude_runs=[
        #     12, 23, 93, 144, 243, 258, 268, 343, 356, 373, 384, 386, 387,
        #     393, 404, 379, 410, 411, 417, 410, 417, 425, 429, 440, 441, 445,
        #     449, 458, 462, 475, 425, 488, 493],
        exclude_runs_reason='No clear AOIs',
        filter_log_k=True,
        path_origin=os.path.join('data', 'choice_task', 'added_var'),
        path_target=os.path.join('data', 'choice_task', 'cleaned'))

    data_subject, data_trial = add_transition_clusters(
        data_trial=data_trial, data_subject=data_subject,
        path_tables=os.path.join('results', 'tables', 'choice_task'),
        undirected_transitions=True, subject_level=True)

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'choice_task', 'cleaned'))

    if new_plots:
        plot_choice_task_heatmap(
            path_origin=os.path.join('data', 'choice_task',
                                     'cleaned', 'data_et.csv'),
            path_target=os.path.join('results', 'plots',
                                     'choice_Task', 'individual_heatmaps',
                                     'selected'))


def analyze_global():
    path_origin = os.path.join('data', 'all_trials', 'cleaned')
    data_et, data_trial, data_subject = load_all_three_datasets(path_origin)

    # Window size
    print(f"""Describe window: \n"""
          f"""{data_subject[['window', 'window_x',
                             'window_y']].describe()} \n""")

    analyze_dropouts(
        path_origin=os.path.join('data', 'all_trials', 'added_var'))

    analyze_demographics()


def analyze_choice():
    path_origin = os.path.join('data', 'choice_task', 'cleaned')
    path_plots = os.path.join('results', 'plots', 'choice_task')
    path_tables = os.path.join('results', 'tables', 'choice_task')

    data_et, data_trial, data_subject = load_all_three_datasets(path_origin)

    # Log K
    print(data_subject['logK'].describe())
    # Done in R
    plot_log_k_frequency(data_subject['logK'])

    # ET Indices
    print(f"""ET Indices: \n"""
          f"""{round(data_subject[['optionIndex', 'attributeIndex',
                                   'payneIndex']].describe(), 2)} \n""")

    for outcome in ['optionIndex', 'attributeIndex', 'payneIndex']:
        plt.hist(x=data_subject[outcome], bins=10)
        plt.title(outcome)
        plt.xlim(-1, 1)
        save_plot(file_name=outcome + '.png',
                  path=os.path.join('results', 'plots', 'choice_task',
                                    'et_indices'))
        plt.close()

    data_subject['student_status'] = data_subject['Student Status']

    predictors = ['chinFirst', 'ethnic', 'degree', 'student_status']

    # Confounders
    get_box_plots(data=data_subject,
                  outcome='choseLL',
                  predictors=predictors,
                  file_name='box_plots_confounders_vs_choseLL.png',
                  path_target=path_plots)

    for predictor in predictors:
        anova_outcomes_factor(data=data_subject,
                              factor=predictor,
                              outcomes=['choseLL'],
                              path=os.path.join(path_tables, 'confounders'))

    t_test_outcomes_vs_factor(data=data_subject,
                              factor='student_status',
                              dependent=False,
                              outcomes=['choseLL'],
                              file_name='t_test_student_vs_choice.csv',
                              path=path_tables)

    plot_example_eye_movement(data_et, data_trial,
                              data_subject['run_id'].unique()[0])

    corr_analysis_choice(data_trial, data_subject, path_plots, path_tables)


def main(new_data=False):
    if new_data:
        create_datasets_from_cognition(
            path_origin=os.path.join('data', 'all_trials', 'cognition_run'),
            path_target=os.path.join('data', 'all_trials', 'combined'))

        integrate_prolific_data(
            file_origin=os.path.join('data', 'all_trials', 'combined',
                                     'data_subject.csv'),
            path_prolific=os.path.join('data', 'prolific'),
            path_target=os.path.join('data', 'all_trials', 'combined'))

    prep_global()
    prep_fix()
    prep_choice()
    analyze_global()
    analyze_fix()
    analyze_choice()

    # Render R markdowns
    subprocess.call(
        ['Rscript', '--vanilla', 'analysis/run_r_markdowns.R'],
        shell=True)


if __name__ == '__main__':
    analyze_fix_task(
        path_plots=os.path.join('results', 'plots', 'fix_task'),
        path_tables=os.path.join('results', 'tables', 'fix_task'),
        path_origin=os.path.join('data', 'fix_task', 'added_var'))
    # main(new_data=False)
