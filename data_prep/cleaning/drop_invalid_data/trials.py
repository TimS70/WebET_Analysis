def clean_trial_duration(data_raw, min_time, max_time, name):
    data = data_raw[
        (data_raw['trial_duration_exact'] > min_time) &
        (data_raw['trial_duration_exact'] < max_time)]

    if len(data) == len(data_raw):
        print(f"""No trials were removed. All trials were in the range """
              f"""{min_time}ms < t < {max_time}ms """)
    else:
        print(f"""Filter reaction time ({min_time} < t < {max_time}) from """
              f"""{name}: \n"""
              f"""   Raw: {len(data_raw)} \n"""
              f"""   Cleaned: {len(data)} \n\n"""
              f"""Average duration raw: \n"""
              f"""{round(data_raw['trial_duration_exact'].describe(), 2)} \n"""
              f"""Average reaction time below 10 seconds: \n"""
              f"""{round(data['trial_duration_exact'].describe(), 2)} \n""")

    return data
