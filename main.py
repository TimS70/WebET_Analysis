import subprocess

import numpy as np
import pandas as pd
import os

from analysis.choice_task.init import analyze_choice_task
from analysis.demographics import analyze_demographics
from analysis.dropouts import dropout_analysis
from analysis.fix_task.data_quality import outcome_over_trials
from analysis.fix_task.init_fix_task_analysis import analyze_fix_task
from analysis.fix_task.positions import compare_positions
from data_prep.add_variables.data_quality import add_data_quality_var
from data_prep.add_variables.init import global_add_variables_to_datasets
from data_prep.add_variables.trial import add_position_index
from data_prep.choice import run_et_cluster_correction, add_variables_to_choice_task_datasets
from data_prep.cleaning.choice import create_choice_data, clean_choice_data
from data_prep.cleaning.init import global_cleaning
from data_prep.cleaning.prolific_ids import drop_duplicate_ids
from data_prep.fix_task import create_fix_tasks_datasets
from data_prep.cleaning.fix_task import clean_fix_task_datasets
from data_prep.load.data_subject_prolific import read_prolific_data, create_data_subject, create_data_prolific
from data_prep.load.init import create_datasets_from_cognition
from data_prep.load.prolific import find_prolific_id_in_raw, combine_cognition_data
from data_prep.load.trial import create_trial_data


def main(new_data=False, cluster_correction=False):
    if new_data:
        create_datasets_from_cognition()

    prep_global_datasets()
    prep_and_analyze_choice_task(cluster_correction=cluster_correction)
    prep_and_analyze_fix_task()

    # Render R markdowns
    subprocess.call(
        ['Rscript', '--vanilla', 'analysis/run_r_markdowns.R'],
        shell=True)


def prep_global_datasets():
    global_add_variables_to_datasets()
    global_cleaning()

    dropout_analysis()
    analyze_demographics()


def prep_and_analyze_choice_task(cluster_correction=False):
    # Prep
    create_choice_data()

    if cluster_correction:
        run_et_cluster_correction()

    add_variables_to_choice_task_datasets(
        use_adjusted_et_data=cluster_correction)

    clean_choice_data(
        use_adjusted_et_data=cluster_correction)

    analyze_choice_task(use_adjusted_et_data=cluster_correction)


def prep_and_analyze_fix_task():
    create_fix_tasks_datasets()
    clean_fix_task_datasets()

    add_data_quality_var()

    analyze_fix_task()


if __name__ == '__main__':
    main()
