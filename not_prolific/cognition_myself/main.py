import os

import pandas as pd

from analysis.main import analyze_fix_task
from data_prep.add_variables.data_quality.main import add_data_quality
from data_prep.add_variables.fit_k.call_from_py import add_log_k
from data_prep.add_variables.main import add_variables_global, \
    add_choice_behavioral_variables, add_aoi_et, add_choice_et_variables
from data_prep.cleaning.all_trials import clean_global_data
from data_prep.cleaning.choice import clean_data_choice
from data_prep.cleaning.fix_task import clean_data_fix
from data_prep.load.choice import load_choice_data
from data_prep.load.fix_task import load_fix_data
from data_prep.load.main import create_datasets_from_cognition
from visualize.choice import plot_choice_task_heatmap
from visualize.eye_tracking import plot_et_scatter


def prep_global():
    create_datasets_from_cognition(
        path_origin=os.path.join('data', 'cognition_myself', 'raw'),
        path_target=os.path.join('data', 'cognition_myself', 'combined'))

    add_variables_global(
        path_origin=os.path.join('data', 'cognition_myself', 'combined'),
        path_target=os.path.join('data', 'cognition_myself', 'added_var'))

    clean_global_data(
        path_origin=os.path.join('data', 'cognition_myself', 'added_var'),
        path_target=os.path.join('data', 'cognition_myself', 'cleaned'),
        prolific=False, approved=False, one_attempt=False,
        max_t_task=5500, min_fps=3,
        exclude_runs=None, exclude_runs_reason=None,
        max_missing_et=10,
        full_runs=True, valid_sight=True,
        follow_instruction=True, correct_webgazer_clock=True,
        complete_fix_task=True)


def prep_fix():
    load_fix_data(path_origin=os.path.join('data', 'cognition_myself',
                                           'cleaned'),
                  path_target=os.path.join('data', 'cognition_myself',
                                           'fix_task', 'raw'))

    clean_data_fix(max_t_task=5500,
                   path_origin=os.path.join('data', 'cognition_myself',
                                            'fix_task', 'raw'),
                   path_target=os.path.join('data', 'cognition_myself',
                                            'fix_task', 'cleaned'))

    add_data_quality(max_offset=0.15,
                     min_hits_per_dot=0.8,
                     path_origin=os.path.join('data', 'cognition_myself',
                                              'fix_task', 'cleaned'),
                     path_target=os.path.join('data', 'cognition_myself',
                                              'fix_task', 'added_var'))


def prep_choice(main_aoi_width=0.4, main_aoi_height=0.4):
    path = os.path.join('data', 'cognition_myself', 'choice_task')
    load_choice_data(path_origin=os.path.join('data', 'cognition_myself',
                                              'cleaned'),
                     path_target=os.path.join(path, 'raw'))

    add_choice_behavioral_variables(
        path_origin=os.path.join(path, 'raw'),
        path_target=os.path.join(path, 'added_var'),
        path_fix_subject=os.path.join('data', 'cognition_myself', 'fix_task',
                                      'added_var'))

    add_aoi_et(aoi_width=main_aoi_width, aoi_height=main_aoi_height,
               path_origin=os.path.join(path, 'raw'),
               path_target=os.path.join(path, 'added_var'))

    data_plot = pd.read_csv(os.path.join(path, 'added_var', 'data_et.csv'))
    data_plot = data_plot[pd.notna(data_plot['aoi'])]
    plot_et_scatter(x=data_plot['x'], y=data_plot['y'],
                    title='AOI raw for all runs ',
                    file_name='aoi_scatter.png',
                    path=os.path.join('results', 'plots', 'cognition_myself'))

    add_choice_et_variables(
        min_required_trials=5, min_gaze_points=3,
        path_origin=os.path.join(path, 'added_var'),
        path_target=os.path.join(path, 'added_var'))

    add_log_k(path=os.path.join(path,
                                'added_var'),
              file_trial_input='data_trial.csv',
              file_subjects_to_merge='data_subject.csv')

    clean_data_choice(us_sample=False,
                      min_hit_ratio=None,  # 0.6,
                      max_precision=None,  # 0.15,
                      max_offset=None,  # 0.5,
                      min_fps=5,
                      min_rt=400, max_rt=10000,
                      min_choice_percentage=None,  # 0.01,
                      max_choice_percentage=None,  # 0.99,
                      exclude_runs=None,
                      exclude_runs_reason=None,
                      filter_log_k=True,
                      path_origin=os.path.join(path, 'added_var'),
                      path_target=os.path.join(path, 'cleaned'))


def analyze_choice():
    plot_choice_task_heatmap(
        path_origin=os.path.join('data', 'cognition_myself', 'choice_task',
                                 'added_var', 'data_et.csv'),
        path_target=os.path.join('results', 'plots', 'cognition_myself',
                                 'heatmaps_choice'))


def analyze_fix():
    analyze_fix_task(
        path_origin=os.path.join('data', 'cognition_myself', 'fix_task',
                                 'added_var'),
        path_plots=os.path.join('results', 'plots', 'fix_task'))


def prep_and_analyze_data_cognition_myself():
    # prep_global()
    # prep_fix()
    # prep_choice()

    analyze_fix()
    # analyze_choice()
