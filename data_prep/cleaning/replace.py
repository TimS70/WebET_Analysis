import numpy as np


def replace_subject_variables(data_subject):
    data_subject = clean_degree(data_subject)
    data_subject['webcam_fps'] = np.round(data_subject['webcam_fps'])

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

    present_categories = np.intersect1d(['middle', 'high', 'college', 'grad'],
                                        data_subject['degree'].unique())

    data_subject['degree'].cat.reorder_categories(present_categories,
                                                  inplace=True)

    print(f"""Replacing education data. New values: \n """
          f"""{data_subject['degree'].unique()} \n""")

    return data_subject
