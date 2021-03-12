import pandas as pd


def runs_not_approved(data_subject):

    unapproved_runs = data_subject.loc[
        ~data_subject['status'].isin(['APPROVED']),
        'run_id'
    ].unique()

    data_not_approved = data_subject.loc[
        data_subject['run_id'].isin(
            unapproved_runs),
        [
            'run_id', 'prolificID', 'max_trial',
            'recorded_date', 'status']
    ]

    rate_unapproved = len(unapproved_runs) / \
        len(data_subject['run_id'].unique())

    n_approved = sum(data_subject['status'].isin(['APPROVED']))

    print(
        f"""n={n_approved} were approved. n={len(unapproved_runs)} """
        f"""({round(100 * rate_unapproved, 2)}%) runs were not approved: \n"""
        f"""{pd.crosstab(index=data_not_approved['status'], columns="n")} \n"""
    )

    return unapproved_runs
