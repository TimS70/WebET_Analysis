def clean_trial_duration(data_raw, min_time, max_time, name):
    data = data_raw[
        (data_raw['trial_duration_exact'] > min_time) &
        (data_raw['trial_duration_exact'] < max_time)]

    print(f"""Filter reaction time ({min_time} < t < {max_time}) from {name}: \n"""
          f"""   Raw: {len(data_raw)} \n"""
          f"""   Cleaned: {len(data)} \n\n"""
          f"""Average duration raw: \n"""
          f"""M = {round(data_raw['trial_duration_exact'].mean(), 2)}, """
          f"""SD = {round(data_raw['trial_duration_exact'].std(), 2)} \n\n"""
          f"""Average reaction time below 10 seconds: \n"""
          f"""M = {round(data['trial_duration_exact'], 2)}, """
          f"""SD = {round(data['trial_duration_exact'], 2)} \n""")

    return data
