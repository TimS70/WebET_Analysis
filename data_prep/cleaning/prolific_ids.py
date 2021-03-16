import pandas as pd


def drop_duplicate_ids(data_subject_raw):
    n_duplicated = data_subject_raw \
        .duplicated(subset=['prolificID']) \
        .sum()

    data_subject = data_subject_raw \
        .sort_values(by=['prolificID', 'max_trial']) \
        .drop_duplicates(subset=['prolificID'], keep='last')

    summary = pd.DataFrame({
        'variable': ['run_id', 'prolific_id'],
        'run_id': [
            len(data_subject_raw['run_id'].unique()),
            len(data_subject['run_id'].unique()),
        ],
        'prolific_id': [

            len(data_subject_raw['prolificID'].unique()),
            len(data_subject['prolificID'].unique())
        ],
        'approved': [
            len(data_subject_raw.loc[
                    data_subject_raw['status'] == 'APPROVED',
                    'run_id'].unique()),
            len(data_subject.loc[
                    data_subject['status'] == 'APPROVED',
                    'prolificID'].unique()),
        ]
    }
    )

    print(
        f"""Removing n={n_duplicated} duplicate ids from data_subject: \n"""
        f"""{summary}\n""")

    return data_subject


def match_ids_with_subjects(data, data_subject, data_name):

    data = data.loc[
           data['run_id'].isin(data_subject['run_id']), :]

    print(
        f"""n={len(data.loc[:, 'run_id'].unique())} runs from {data_name} """
        f"""were also in data_subject. """)

    return data
