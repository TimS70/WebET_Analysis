import subprocess

from analysis.choice_task.init_choice_analysis import analyze_choice_task
from analysis.demographics import analyze_demographics
from analysis.dropouts import dropout_analysis
from analysis.fix_task.init_fix_task_analysis import analyze_fix_task
from data_prep.add_variables.data_quality import add_data_quality_var
from data_prep.add_variables.init import global_add_variables_to_datasets
from data_prep.choice import add_variables_choice_task, add_log_k
from data_prep.cleaning.choice import create_choice_data, clean_choice_data
from data_prep.cleaning.fix_task import clean_fix_task_datasets
from data_prep.cleaning.init import global_cleaning
from data_prep.fix_task import create_fix_tasks_datasets
from data_prep.load.init import create_datasets_from_cognition


def main(new_data=False):
    if new_data:
        create_datasets_from_cognition()

    prep_global_datasets()
    prep_and_analyze_fix_task()
    prep_and_analyze_choice_task()

    # Render R markdowns
    subprocess.call(
        ['Rscript', '--vanilla', 'analysis/run_r_markdowns.R'],
        shell=True)


def prep_global_datasets():
    global_add_variables_to_datasets()
    global_cleaning()

    dropout_analysis()
    analyze_demographics()


def prep_and_analyze_choice_task():
    # Prep
    create_choice_data()

    # run_et_cluster_correction()

    add_variables_choice_task()

    add_log_k()

    clean_choice_data()

    analyze_choice_task()


def prep_and_analyze_fix_task():
    create_fix_tasks_datasets()
    clean_fix_task_datasets()

    add_data_quality_var()

    analyze_fix_task()


if __name__ == '__main__':
    # Render R markdowns
    subprocess.call(
        ['Rscript', '--vanilla', 'analysis/run_r_markdowns.R'],
        shell=True)

    # main(new_data=False)
