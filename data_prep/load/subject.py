from data_prep.load.survey_data import create_survey_data


def create_data_subject(data_raw):
    data_subject = data_raw[[
        'run_id', 'chinFirst', 'choiceTask_amountLeftFirst',
        'browser', 'browser_version', 'device',
        'platform', 'platform_version', 'user_agent',
        'chosenAmount', 'chosenDelay',
        'webcam_label', 'webcam_fps', 'webcam_height', 'webcam_width']
    ].drop_duplicates()

    survey_data = create_survey_data(data_raw)

    data_subject = data_subject \
        .merge(survey_data, on='run_id', how='left') \
        .rename(columns={'age': 'birthyear'})

    return data_subject
