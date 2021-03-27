import subprocess

from amasino.main import prep_data
from analysis.demographics import analyze_demographics
from analysis.dropouts.main import analyze_dropouts
from analysis.main import analyze_fix_task, analyze_choice_task
from data_prep.add_variables.data_quality.main import add_data_quality
from data_prep.add_variables.main import add_variables_global, add_variables_choice
from data_prep.load.choice import load_choice_data
from data_prep.cleaning.main import clean_global_data, clean_data_fix, clean_data_choice
from data_prep.load.fix_task import load_fix_data
from data_prep.load.main import create_datasets_from_cognition

from data_prep.add_variables.fit_k.call_from_py import add_log_k


def prep_data():
    # add_variables_global()
    clean_global_data(max_t_task=5500, min_fps=3)

    load_fix_data()
    clean_data_fix(max_t_task=5500)
    add_data_quality(max_offset=0.15, min_hits_per_dot=0.8)

    load_choice_data()
    # run_et_cluster_correction()

    add_variables_choice(
        aoi_width=0.5, aoi_height=0.5,
        min_required_trials=5,
        min_gaze_points=3)

    add_log_k()

    clean_data_choice(
        min_hit_ratio=0.6, max_precision=0.15,
        max_offset=0.5, min_fps=5,
        min_rt=400, max_rt=10000,
        min_choice_percentage=0.01,
        max_choice_percentage=0.99)


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

    prep_data()
    analyze()


if __name__ == '__main__':
    main(new_data=False)
