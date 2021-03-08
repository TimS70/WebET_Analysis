from analysis.dropouts import dropout_analysis
from data_prep.add_variables.init import global_add_variables_to_datasets
from data_prep.cleaning.choice import create_and_clean_choice_data
from data_prep.fix_task import create_fix_tasks_datasets
from data_prep.cleaning.fix_task import clean_fix_task_datasets


def main():
    # Global
    # TODO: Use if statements and function parameters
    # create_datasets_from_cognition()

    # global_add_variables_to_datasets()

    # dropout_analysis()

    # Choice data
    create_and_clean_choice_data()

    # run_et_cluster_correction()

    # add_variables_to_choice_task_datasets(use_adjusted_et_data=True)

    # Analyze Choice task
    # analyze_choice_task(use_adjusted_et_data = True)

    create_fix_tasks_datasets()
    clean_fix_task_datasets()


if __name__ == '__main__':
    main()
