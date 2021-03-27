def choice_response_variables(data):
    # Up-Arrow is 38, Down-Arrow is 40
    data["choseTop"] = 0
    data.loc[(data["key_press"] == 38), "choseTop"] = 1

    data["choseLL"] = 0
    data.loc[(data["choseTop"] == 1) & (data["LL_top"] == 1), "choseLL"] = 1
    data.loc[(data["choseTop"] == 0) & (data["LL_top"] == 0), "choseLL"] = 1

    print(
        f"""Add choice response variables \n"""
        f"""{data.loc[:, 
             ['key_press', 'LL_top', 'choseTop', 'choseLL']]} \n"""
    )
    return data


def add_mean_choice_rt(data_subject, data_trial):
    grouped = data_trial.groupby(['run_id'])['trial_duration_exact'].mean() \
        .reset_index() \
        .rename(columns={'trial_duration_exact': 'choice_rt'})

    if 'choice_rt' in data_subject.columns:
        data_subject = data_subject.drop(columns=['choice_rt'])
    data_subject = data_subject.merge(grouped, on='run_id', how='left')

    print(
        f"""Added choice_rt: \n"""
        f"""{data_subject['choice_rt'].describe()}\n"""
    )

    return data_subject
