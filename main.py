from analysis.choice_task import analyze_choice_task
from analysis.demographics import show_demographics
from analysis.dropouts import dropout_analysis
from analysis.fix_task.init import analyze_fix_task
from data_prep.add_variables.data_quality import add_data_quality_var
from data_prep.add_variables.init import global_add_variables_to_datasets
from data_prep.choice import run_et_cluster_correction, add_variables_to_choice_task_datasets
from data_prep.cleaning.choice import create_and_clean_choice_data
from data_prep.cleaning.init import global_cleaning
from data_prep.fix_task import create_fix_tasks_datasets
from data_prep.cleaning.fix_task import clean_fix_task_datasets
from data_prep.load.init import create_datasets_from_cognition


def main(new_data=False, cluster_correction=False):
    # create_data(new_data=new_data)
    init_analysis(cluster_correction=cluster_correction)


def create_data(new_data=False):
    if new_data:
        # create_datasets_from_cognition()
        global_add_variables_to_datasets()
        global_cleaning()

        create_and_clean_choice_data()

        create_fix_tasks_datasets()
        clean_fix_task_datasets()
        add_data_quality_var()


def init_analysis(cluster_correction=False):

    # dropout_analysis()
    # show_demographics()

    # Choice data
    # if cluster_correction:
    #    run_et_cluster_correction()

    # add_variables_to_choice_task_datasets(
    #     use_adjusted_et_data=cluster_correction)
    # analyze_choice_task(
    #     use_adjusted_et_data=cluster_correction)

    # Fix task
    analyze_fix_task()


if __name__ == '__main__':
    main(new_data=True, cluster_correction=True)
