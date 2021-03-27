import subprocess

from amasino.main import prep_data
from analysis.demographics import analyze_demographics
from analysis.dropouts.main import analyze_dropouts
from analysis.main import analyze_fix_task, analyze_choice_task
from data_prep.add_variables.data_quality.main import add_data_quality
from data_prep.add_variables.main import add_variables_global, add_variables_choice
from data_prep.load.choice import load_choice_data
from data_prep.cleaning.main import clean_data_global, clean_data_fix, clean_data_choice
from data_prep.load.fix_task import load_fix_data
from data_prep.load.main import create_datasets_from_cognition

from data_prep.add_variables.fit_k.call_from_py import add_log_k


def prep_data():
    add_variables_global()
    clean_data_global()

    load_fix_data()
    clean_data_fix()
    add_data_quality()

    load_choice_data()
    # run_et_cluster_correction()
    add_variables_choice()
    add_log_k()
    clean_data_choice()


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
    add_log_k()
    clean_data_choice()
    analyze()
    # main(new_data=False)
