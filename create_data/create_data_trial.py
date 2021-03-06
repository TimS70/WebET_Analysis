def create_data_trial(data_raw):

    data_trial = data_raw.loc[
                 :,
                 [
                     'run_id', 'prolificID', 'subject', 'chinFirst',
                     'trial_index',
                     'trial_type', 'task_nr',
                     'rt', 'stimulus', 'key_press',
                     'time_elapsed', 'trial_duration', 'recorded_at',
                     'window_width', 'window_height', 'success',

                     'chin', 'x_pos', 'y_pos',

                     'choiceTask_amountLeftFirst',
                     'option_topLeft', 'option_bottomLeft',
                     'option_topRight', 'option_bottomRight',
                     'chosenAmount', 'chosenDelay',
                 ]
                 ]

    columns = [
        'run_id', 'subject', 'chinFirst', 'chin', 'task_nr', 'trial_index',  # Int
        'key_press',
        'x_pos', 'y_pos', 'time_elapsed', 'trial_duration',
        'rt',
        'window_width', 'window_height'
    ]

    for col in columns:
        data_trial[col] = data_trial[col].replace({'"': np.nan})
        data_trial[col] = pd.to_numeric(data_trial[col])

    if not os.path.exists('./data_jupyter/raw'):
        os.mkdir('./data_jupyter/raw')

    data_trial.to_csv(
        "data_jupyter/raw/data_trial.csv",
        index=False, header=True)

    print('data_trial saved!')

    return data_trial