import pandas as pd

def check_unequal_trial_numbers(data_et, data_trial):
    et_trials = data_et.groupby(
        ['run_id', 'trial_index'],
        as_index=False)['x'].count() \
        .rename(columns={'x': 'x_count_2'})

    data_trial_added_count_2 = data_trial.merge(
        et_trials, on=['run_id', 'trial_index'], how='left')

    grouped_missing_et = data_trial_added_count_2.loc[
                         pd.isna(data_trial_added_count_2['x_count_2']), :] \
        .groupby(['run_id'], as_index=False)['trial_index'].count()

    if len(grouped_missing_et) > 0:
        print(f"""{len(grouped_missing_et)} runs have at least one """
              f"""empty (et-related) trial. \n"""
              f"""That is where the difference of """
              f"""{grouped_missing_et['trial_index'].sum()} trials """
              f"""is coming from: \n"""
              f"""{grouped_missing_et} \n""")
    else:
        print('No difference in trial number found')
