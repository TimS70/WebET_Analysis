import pandas as pd


def filter_approved(data, data_subject):
    unapproved_runs = runs_not_approved(data_subject)

    data = data.loc[
       ~data['run_id'].isin(unapproved_runs), :]

    print(f"""Removed n = {len(unapproved_runs)} runs. \n""")

    return data


def runs_not_approved(data_subject):
    unapproved_runs = data_subject.loc[
        ~data_subject['status'].isin(['APPROVED']),
        'prolificID'
    ].unique()

    data_not_approved = data_subject.loc[
        data_subject['prolificID'].isin(
            unapproved_runs),
        [
            'run_id', 'prolificID', 'max_trial',
            'recorded_date', 'status']
    ]

    rate_unapproved = len(unapproved_runs) / \
        len(data_subject['run_id'].unique())

    print(
        f"""n = {len(unapproved_runs)} """
        f"""({round(100 * rate_unapproved, 2)}%) runs were not approved: \n"""
        f"""{pd.crosstab(index=data_not_approved['status'], columns="n")} \n"""
    )

    return unapproved_runs
