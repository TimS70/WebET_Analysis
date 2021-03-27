def clean_runs(data_raw, excluded_runs, name):

    data = data_raw.loc[~data_raw['run_id'].isin(excluded_runs), :]

    print(
        f"""Removing invalid runs from {name}: \n"""
        f"""   Raw: {len(data_raw['run_id'].unique())} \n"""
        f"""   Cleaned: {len(data['run_id'].unique())} \n""")

    return data

