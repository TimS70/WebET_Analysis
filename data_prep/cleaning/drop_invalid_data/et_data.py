import pandas as pd


def drop_na_data_et(data_et):

    na_data = data_et[
        pd.isna(data_et['x']) |
        pd.isna(data_et['y'])]

    if len(na_data) < 1:
        print(f'No gaze points with missing eye-tracking data were found. \n')
    else:
        print(f'{len(na_data)} empty gaze points were excluded. \n')

    data_et = data_et[
              pd.notna(data_et['x']) |
              pd.notna(data_et['y'])]

    return data_et
