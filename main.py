import os
import subprocess

from analysis.demographics import analyze_demographics
from analysis.dropouts.main import analyze_dropouts
from analysis.main import analyze_fix_task, analyze_choice_task
from data_prep.add_variables.data_quality.main import add_data_quality
from data_prep.add_variables.fit_k.call_from_py import add_log_k
from data_prep.add_variables.main import add_choice_behavioral_variables, \
    add_choice_et_variables, add_aoi_et, add_variables_global
from data_prep.add_variables.prolific import add_prolific_variables
from data_prep.cleaning.all_trials import clean_global_data
from data_prep.cleaning.fix_task import clean_data_fix
from data_prep.cleaning.choice import clean_data_choice
from data_prep.clustering.main import init_cluster_correction
from data_prep.load.choice import load_choice_data
from data_prep.load.fix_task import load_fix_data
from data_prep.load.main import create_datasets_from_cognition, \
    integrate_prolific_data
from not_prolific.cognition_myself.main import prep_data_cognition_myself
from visualize.choice import plot_choice_task_heatmap


def prepare_datasets(main_aoi_width=0.4, main_aoi_height=0.4,
                     correct_clusters=False):

    add_variables_global(
        path_origin=os.path.join('data', 'all_trials', 'combined'),
        path_target=os.path.join('data', 'all_trials', 'added_var'))

    add_prolific_variables(
        path_origin=os.path.join('data', 'all_trials', 'combined'),
        path_target=os.path.join('data', 'all_trials', 'added_var'))

    runs_no_saccade = [144, 171, 380]
    clean_global_data(
        path_origin=os.path.join('data', 'all_trials', 'added_var'),
        path_target=os.path.join('data', 'all_trials', 'cleaned'),
        prolific=True, approved=True, one_attempt=True,
        max_t_task=5500, min_fps=3,
        exclude_runs=runs_no_saccade, max_missing_et=10,
        full_runs=True, valid_sight=True,
        follow_instruction=True, correct_webgazer_clock=True,
        complete_fix_task=True)

    load_fix_data(path_origin=os.path.join('data', 'all_trials', 'cleaned'),
                  path_target=os.path.join('data', 'fix_task', 'raw'))

    clean_data_fix(max_t_task=5500,
                   path_origin=os.path.join('data', 'fix_task', 'raw'),
                   path_target=os.path.join('data', 'fix_task', 'cleaned'))

    add_data_quality(max_offset=0.15,
                     min_hits_per_dot=0.8,
                     path_origin=os.path.join('data', 'fix_task', 'cleaned'),
                     path_target=os.path.join('data', 'fix_task', 'added_var'))

    load_choice_data(path_origin=os.path.join('data', 'all_trials', 'cleaned'),
                     path_target=os.path.join('data', 'choice_task', 'raw'))

    add_choice_behavioral_variables(
        path_origin=os.path.join('data', 'choice_task', 'raw'),
        path_target=os.path.join('data', 'choice_task', 'added_var'),
        path_fix_subject=os.path.join('data', 'fix_task', 'added_var'))

    # eye-tracking
    plot_choice_task_heatmap(
        path_origin=os.path.join('data', 'choice_task',
                                 'raw', 'data_et.csv'),
        path_target=os.path.join('results', 'plots',
                                 'clustering', 'py_clusters',
                                 'heatmaps_all'))

    add_aoi_et(aoi_width=main_aoi_width, aoi_height=main_aoi_height,
               path_origin=os.path.join('data', 'choice_task', 'raw'),
               path_target=os.path.join('data', 'choice_task', 'added_var'))

    if correct_clusters:
        data_et_corrected = init_cluster_correction(
            distance_threshold=0.25,
            min_cluster_size=50,
            min_ratio=0.5,
            max_deviation=0.25,
            aoi_width=main_aoi_width,
            aoi_height=main_aoi_height,
            message=False,
            path_origin=os.path.join('data', 'choice_task', 'added_var'),
            path_target=os.path.join('data', 'choice_task', 'added_var'))

        plot_choice_task_heatmap(
            path_origin=os.path.join('data', 'choice_task',
                                     'raw', 'data_et.csv'),
            path_target=os.path.join('results', 'plots',
                                     'clustering', 'py_clusters',
                                     'heatmaps_selected'),
            runs=data_et_corrected['run_id'].unique())

    add_choice_et_variables(
        min_required_trials=5, min_gaze_points=3,
        path_origin=os.path.join('data', 'choice_task', 'added_var'),
        path_target=os.path.join('data', 'choice_task', 'added_var'))

    add_log_k(file_origin=os.path.join('data', 'choice_task', 'added_var',
                                       'data_trial.csv'),
              file_merge_to=os.path.join('data', 'choice_task', 'added_var',
                                         'data_subject.csv'))

    clean_data_choice(
        us_sample=False,
        min_hit_ratio=None,  # 0.6,
        max_precision=None,  # 0.15,
        max_offset=None,  # 0.5,
        min_fps=5,
        min_rt=400, max_rt=10000,
        min_choice_percentage=None,  # 0.01,
        max_choice_percentage=None,  # 0.99,
        exclude_runs=[
            12, 23, 93, 144, 243, 258, 268, 343, 356, 373, 384, 386, 387,
            393, 404, 379, 410, 411, 417, 410, 417, 425, 429, 440, 441, 445,
            449, 458, 462, 475, 425, 488, 493],
        filter_log_k=False,
        path_origin=os.path.join('data', 'choice_task', 'added_var'),
        path_target=os.path.join('data', 'choice_task', 'cleaned'))


def analyze():
    analyze_dropouts()
    analyze_demographics()
    analyze_fix_task()
    analyze_choice_task()

    # Render R markdowns
    subprocess.call(
        ['Rscript', '--vanilla', 'analysis/run_r_markdowns.R'],
        shell=True)


def main(new_data=False):
    if new_data:
        create_datasets_from_cognition(
            path_origin=os.path.join('data', 'all_trials', 'cognition_run'),
            path_target=os.path.join('data', 'all_trials', 'combined'))

        integrate_prolific_data(
            path_origin=os.path.join('data', 'all_trials', 'cognition_run'),
            path_target=os.path.join('data', 'all_trials', 'combined'))

    prepare_datasets()
    analyze()


if __name__ == '__main__':
    prep_data_cognition_myself()
    # main(new_data=False)
