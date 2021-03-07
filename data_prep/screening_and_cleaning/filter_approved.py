import pandas as pd


def filter_approved(data, data_subject):
    unapproved_runs = runs_not_approved(data_subject)

    data = data.loc[
                   ~data['run_id'].isin(unapproved_runs),
                   :]

    return data


def runs_not_approved(data_subject):
    unapproved_runs = data_subject.loc[
        ~data_subject['status'].isin(['APPROVED']),
        'prolificID'
    ].unique()

    print(data_subject.columns)
    data_not_approved = data_subject.loc[
        data_subject['prolificID'].isin(unapproved_runs),
        ['run_id', 'prolificID', 'max_trial', 'recorded_date', 'status']
    ]
    print(
        f"""N Subjects that are not approved: {len(unapproved_runs)} """
        f"""= {round(100 * len(unapproved_runs) / len(data_subject['run_id'].unique()), 2)}%"""
    )

    print(f'data_not_approved: {data_not_approved}')

    return unapproved_runs


