import pandas as pd


def missing_glasses(data_subject):
    runs_na_glasses = data_subject.loc[
        pd.isna(data_subject['glasses_binary']),
        'run_id']

    if len(runs_na_glasses) > 0:
        print(
            f"""n={len(runs_na_glasses)} """
            f"""participants were excluded because we did not provide """
            f"""information about their sight. \n""")
    else:
        print('Checked sight-information of subjects and found no '
              'missing data. \n')

    return runs_na_glasses


def filter_runs_bad_time_measure(data_trial, max_t_task):
    grouped_time_by_trial = data_trial.loc[
        data_trial['trial_duration_exact'] > max_t_task, :] \
            .groupby(
                ['run_id', 'trial_index'],
                as_index=False)['trial_duration_exact'].mean()

    runs_with_long_trials = grouped_time_by_trial \
        .groupby(
            ['run_id'],
            as_index=False)['trial_index'].count() \
        .rename(columns={'trial_index': 'n'}) \
        .sort_values(by='n')

    summary_1 = grouped_time_by_trial.groupby(
            ['run_id'],
            as_index=False)['trial_index'].count() \
        .rename(columns={'trial_index': 'n_long_trials'})

    print(
        f"""n={len(runs_with_long_trials)} runs with long trials """
        f"""(> {max_t_task}ms): \n"""
        f"""{summary_1} \n""")

    runs_bad_time_measure = runs_with_long_trials.loc[
        runs_with_long_trials['n'] > 3,
        'run_id']

    summary_2 = grouped_time_by_trial.loc[
        grouped_time_by_trial['run_id'].isin(runs_bad_time_measure), :] \
        .groupby(
            ['run_id'],
            as_index=False)['trial_index'].count() \
        .rename(columns={'trial_index': 'n_long_trials'})

    print(
        f"""n={len(runs_bad_time_measure)} runs with bad time measure """
        f"""(>3 trials longer than {max_t_task}ms): \n"""
        f"""{summary_2} \n""")

    return runs_bad_time_measure


def runs_with_incomplete_fix_tasks(data_trial_fix):
    n_trials_by_run = data_trial_fix \
        .groupby(['run_id'], as_index=False)['trial_index'].count() \
        .rename(columns={'trial_index': 'n'})

    runs_incomplete_fix_task = n_trials_by_run.loc[
        n_trials_by_run['n'] < 18, 'run_id']

    summary = n_trials_by_run.loc[
              n_trials_by_run['run_id'].isin(runs_incomplete_fix_task),
              :]

    if len(summary) > 0:
        print(
            f"""Runs without the full number of trials: \n"""
            f"""{summary} \n""")
    else:
        print(f"""No runs without the full number of trials found. \n""")

    return runs_incomplete_fix_task
