


def exclude_na_data_et(data_et):

    na_data = data_et.loc[
        pd.isna(data_et['x']) |
        pd.isna(data_et['y']),
        :]

    if len(na_data)<1:
        print(f'No missing data in data_et!')
    else:
        print(f'{len(na_data)} empty gaze points were excluded.')

    data_et = data_et.loc[
              pd.notna(data_et['x']) |
              pd.notna(data_et['y']),
              :]

    return data_et