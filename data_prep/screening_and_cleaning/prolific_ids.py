import pandas as pd


def clean_prolific_ids(data_subject):
    data_subject = drop_duplicate_ids(data_subject)
    data_subject = drop_missing_prolific_ids(data_subject)

    return data_subject


def drop_duplicate_ids(data_subject):
    n_duplicated = data_subject \
        .duplicated(subset=['prolificID']) \
        .sum()

    print(f'Number of duplicate prolific IDs: {n_duplicated}')

    data_subject = data_subject \
        .sort_values(by=['prolificID', 'max_trial']) \
        .drop_duplicates(subset=['prolificID'], keep='last')

    return data_subject


def drop_missing_prolific_ids(data):
    print(data.loc[
              pd.isna(data['prolificID']),
              ['run_id', 'prolificID', 'browser', 'recorded_date']
          ])
    data = data.loc[pd.notna(data['prolificID']), :]

    return data


def match_ids_with_subjects(data, data_subject):

    data = data.loc[
           data['run_id'].isin(data_subject['run_id']),
              :]

    print(
        f"""match_ids_with_subjects """
        f"""{len(data.loc[:, 'run_id'].unique())}""")

    return data
