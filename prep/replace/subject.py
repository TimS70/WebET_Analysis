import numpy as np
import pandas as pd


def clean_subject_variables(data_subject):
    data_subject = clean_degree(data_subject)
    data_subject['webcam_fps'] = np.round(data_subject['webcam_fps'])

    return data_subject


def clean_degree(data_subject):
    data_subject['degree'] = data_subject['degree'] \
        .replace(
        ['-3.0', '0', '1.25', '1.5', '2', '4.25'],
        np.nan
    )

    data_subject['degree'] = data_subject['degree'].replace({
        'Middle School': 'middle',
        'middleSchool': 'middle',
        'High School': 'high',
        'high school': 'high',
        'highSchool': 'high',
        'Associates Degree': 'high',
        'Associate ': 'high',

        'College / Undergraduate / Bachelor': 'college',
        'Bachelor': 'college',

        'masters degree': 'grad',
        'graduate': 'grad',
        'Grad': 'grad',
        'Graduate / PhD / Master': 'grad',
        'masters degree': 'grad',
    })
    data_subject['degree'] = data_subject['degree'].astype('category')
    data_subject['degree'].cat.reorder_categories(
        ['middle', 'high', 'college', 'grad'], inplace=True)

    return data_subject