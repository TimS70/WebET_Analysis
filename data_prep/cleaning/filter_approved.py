import pandas as pd

from utils.tables import summarize_datasets


def filter_approved_runs(data_subject, data_trial, data_et):

    ids_not_approved = data_subject.loc[
        ~data_subject['status'].isin(['APPROVED']), 'prolificID'].unique()

    data_not_approved = data_subject.loc[
        data_subject['prolificID'].isin(ids_not_approved),[
            'run_id', 'prolificID', 'max_trial',
            'recorded_date', 'status']]

    rate_unapproved = len(ids_not_approved) / \
        len(data_subject['prolificID'].unique())

    ids_approved = len(data_subject.loc[
                         data_subject['status'].isin(['APPROVED']),
                         'prolificID'].unique())

    print(
        f"""n={ids_approved} were approved. n={len(ids_not_approved)} """
        f"""({round(100 * rate_unapproved, 2)}%) runs were not approved: \n"""
        f"""nan: {sum(pd.isna(data_subject['status']))} \n"""
        f"""{pd.crosstab(index=data_not_approved['status'], columns="n")} \n"""
    )

    data_subject = data_subject.loc[data_subject['status'] == 'APPROVED', :]

    data_trial = data_trial.loc[
        data_trial['prolificID'].isin(data_subject['prolificID']), :]

    data_et = data_et.loc[
        data_et['run_id'].isin(data_subject['run_id']), :]

    print('Filtered approved Prolific IDs:')
    summarize_datasets(data_et, data_trial, data_subject)

    return data_subject, data_trial, data_et
