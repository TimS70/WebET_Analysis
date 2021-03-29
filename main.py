import os
import subprocess

from analysis.demographics import analyze_demographics
from analysis.dropouts.main import analyze_dropouts
from analysis.main import analyze_fix_task, analyze_choice_task
from data_prep.add_variables.data_quality.main import add_data_quality
from data_prep.add_variables.fit_k.call_from_py import add_log_k
from data_prep.add_variables.main import add_choice_behavioral_variables, \
    add_choice_et_variables, add_aoi_et, add_variables_global
from data_prep.cleaning.main import clean_global_data, clean_data_fix, \
    clean_data_choice
from data_prep.cluster_py.main import init_cluster_correction
from data_prep.load.choice import load_choice_data
from data_prep.load.fix_task import load_fix_data
from data_prep.load.main import create_datasets_from_cognition
from visualize.choice import plot_choice_task_heatmap


def prepare_datasets(main_aoi_width=0.4, main_aoi_height=0.4,
                     correct_clusters=True):

    add_variables_global()
    clean_global_data(max_t_task=5500,
                      min_fps=3)

    load_fix_data(
        origin_path=os.path.join('data', 'all_trials', 'cleaned'))

    clean_data_fix(max_t_task=5500)
    add_data_quality(max_offset=0.15,
                     min_hits_per_dot=0.8)

    load_choice_data(
        origin_path=os.path.join('data', 'all_trials', 'cleaned'))

    add_choice_behavioral_variables()

    # eye-tracking
    plot_choice_task_heatmap(
        path_origin=os.path.join('data', 'choice_task',
                                 'raw', 'data_et.csv'),
        path_target=os.path.join('results', 'plots',
                                 'clustering', 'py_clusters',
                                 'heatmaps_all'))

    add_aoi_et(aoi_width=main_aoi_width,
               aoi_height=main_aoi_height)

    if correct_clusters:
        data_et_corrected = init_cluster_correction(
            distance_threshold=0.25,
            min_cluster_size=50,
            min_ratio=0.5,
            max_deviation=0.25,
            aoi_width=main_aoi_width,
            aoi_height=main_aoi_height,
            message=False)

        plot_choice_task_heatmap(
            path_origin=os.path.join('data', 'choice_task',
                                     'raw', 'data_et.csv'),
            path_target=os.path.join('results', 'plots',
                                     'clustering', 'py_clusters',
                                     'heatmaps_selected'),
            runs=data_et_corrected['run_id'].unique())

    add_choice_et_variables(min_required_trials=5,
                            min_gaze_points=3)

    add_log_k()

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
        filter_log_k=False)


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
        create_datasets_from_cognition()

    prepare_datasets()
    analyze()


if __name__ == '__main__':
    main(new_data=False)
