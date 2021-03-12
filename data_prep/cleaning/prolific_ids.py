import pandas as pd


def drop_duplicate_ids(data_subject):
    n_duplicated = data_subject \
        .duplicated(subset=['prolificID']) \
        .sum()

    print(f'n={n_duplicated} runs with duplicate Prolific IDs. ')

    data_subject = data_subject \
        .sort_values(by=['prolificID', 'max_trial']) \
        .drop_duplicates(subset=['prolificID'], keep='last')

    return data_subject


def match_ids_with_subjects(data, data_subject, data_name):

    data = data.loc[
           data['run_id'].isin(data_subject['run_id']), :]

    print(
        f"""n={len(data.loc[:, 'run_id'].unique())} overlapping """
        f"""runs between data_subject and {data_name}. """)

    return data
