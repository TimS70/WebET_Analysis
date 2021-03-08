from analysis.dropouts import dropout_analysis
from data_prep.add_variables.choice import add_variables_to_choice_task_datasets, run_et_cluster_correction
from data_prep.add_variables.init import global_add_variables_to_datasets
from data_prep.screening_and_cleaning.choice import clean_choice_data


def main():
    # Global
    # TODO: Use if statements and function parameters
    # create_datasets_from_cognition()

    # global_add_variables_to_datasets()

    # dropout_analysis()

    # Choice data
    # clean_choice_data()

    run_et_cluster_correction()

    # add_variables_to_choice_task_datasets(use_adjusted_et_data=False)


if __name__ == '__main__':
    main()
