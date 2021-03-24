import subprocess

from analysis.demographics import analyze_demographics
from analysis.dropouts.main import analyze_dropouts
from analysis.main import analyze_fix_task, analyze_choice_task
from data_prep.add_variables.data_quality import add_data_quality
from data_prep.add_variables.init import global_add_variables_to_datasets
from data_prep.choice import add_variables_choice, add_log_k
from data_prep.cleaning.choice import create_choice_data, clean_choice_data
from data_prep.cleaning.fix_task import clean_fix_task_datasets
from data_prep.cleaning.init import global_cleaning
from data_prep.fix_task import create_fix_tasks_datasets
from data_prep.load.init import create_datasets_from_cognition


def main(new_data=False):
    if new_data:
        create_datasets_from_cognition()

    prep_data()
    analyze()


def prep_data():
    global_add_variables_to_datasets()
    global_cleaning()

    create_fix_tasks_datasets()
    clean_fix_task_datasets()
    add_data_quality()

    create_choice_data()
    # run_et_cluster_correction()
    add_variables_choice()
    add_log_k()
    clean_choice_data()


def analyze():
    analyze_dropouts()
    analyze_demographics()
    analyze_fix_task()
    analyze_choice_task()

    # Render R markdowns
    subprocess.call(
        ['Rscript', '--vanilla', 'analysis/run_r_markdowns.R'],
        shell=True)


if __name__ == '__main__':
    analyze_dropouts()
    # main(new_data=False)
