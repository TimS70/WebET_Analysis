import pandas as pd
import sys

if sys.version_info[0] < 3:
    pass
else:
    pass
from tqdm import tqdm

from utils.path import makedir


def create_et_data(data):
    data_et = pd.DataFrame(columns=['x', 'y', 't'])
    data["et_data"] = data['et_data'].apply(str)

    et_indices = data.loc[
                 (pd.notna(data['et_data'])) &
                 ~(data['et_data'].isin(['"', '[]', 'nan'])),
                 :].index

    for i in tqdm(et_indices,
                  desc='Create eye-tracking data'):
        df = text_to_data_frame(data.loc[i, 'et_data'])

        df["t_task"] = (df.loc[:, "t"] - df.loc[0, "t"])
        df['run_id'] = data.loc[i, 'run_id']
        df['trial_index'] = data.loc[i, 'trial_index']

        data_et = data_et.append(pd.DataFrame(data=df), ignore_index=True)

    makedir('data', 'all_trials', 'combined')
    data_et.to_csv("data/all_trials/combined/data_et.csv",
                   index=False, header=True)
    print('data_et saved!')

    return data_et


def text_to_data_frame(text):
    text = text.replace('$', ',')
    dataframe = pd.read_json(text, orient='records')
    return dataframe
