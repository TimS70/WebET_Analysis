import numpy as np
import pandas as pd
import os

from utils.save_data import write_csv


def clean_subject_variables(path_origin, path_target):
    data_subject = pd.read_csv(os.path.join(path_origin, 'data_subject.csv'))
    data_subject = clean_degree(data_subject)

    data_subject['optionalNote'] = data_subject[['optionalNote']].astype(str)

    data_subject = data_subject[[
        'run_id', 'prolificID', 'chinFirst', 'choiceTask_amountLeftFirst',
        'browser',
        # Unnecessary technical details
        # 'browser_version', 'device', 'platform', 'platform_version',
        # 'user_agent', 'webcam_label',
        'chosenAmount', 'chosenDelay',
        'webcam_fps', 'webcam_height', 'webcam_width',
        'birthyear', 'gender', 'ethnic',
        'sight', 'glasses', 'degree',
        'eyeshadow', 'masquara', 'eyeliner', 'browliner',
        'vertPosition', 'triedChin', 'keptHead', 'optionalNote',
        # Unnecessary Prolific details
        # 'session_id', 'age', 'prolific_score', 'reviewed_at_datetime',
        # 'entered_code', 'Webcam',
        'num_approvals', 'num_rejections', 'status', 'recorded_date',
        'Country of Birth', 'Current Country of Residence',
        'Employment Status', 'First Language',
        'Nationality', 'Sex', 'Student Status',
        'Autistic Spectrum Disorder', 'fps', 'max_trial', 'glasses_binary',
        'employment_status', 'fullTime_binary']]

    data_subject['webcam_fps'] = np.round(data_subject['webcam_fps'])

    write_csv(data_subject, 'data_subject.csv', path_target)

    return data_subject


def clean_degree(data_subject):
    data_subject['degree'] = data_subject['degree'] \
        .replace(['-3.0', '0', '1.25', '1.5', '2', '4.25'], np.nan) \
        .replace(['Middle School', 'middleSchool'], 'middle') \
        .replace(['High School', 'high school', 'highSchool',
                  'Associates Degree', 'Associate '], 'high') \
        .replace(['College / Undergraduate / Bachelor', 'Bachelor'], 'college') \
        .replace(['masters degree', 'graduate', 'Grad',
                  'Graduate / PhD / Master'], 'grad') \
        .astype('category')

    # present_categories = np.intersect1d(
    #     ['middle', 'high', 'college', 'grad'],
    #     data_subject.loc[pd.notna(data_subject['degree']), 'degree'].unique())

    data_subject['degree'].cat.reorder_categories(
        ['middle', 'high', 'college', 'grad'],
        inplace=True)

    print(f"""Replacing education data. New values: \n """
          f"""{data_subject['degree'].unique()} \n""")

    return data_subject
