import json
import sys
from functools import partial
import numpy as np
import pandas as pd

if sys.version_info[0] < 3:
    pass
else:
    pass
from tqdm import tqdm


def create_et_data_2(data, n_bins=5):
    data["et_data"] = data['et_data'] \
        .apply(str) \
        .str.replace('$', ',', regex=False)

    et_indices = data[(pd.notna(data['et_data'])) &
                      ~(data['et_data'].isin(['"', '[]', 'nan']))].index
    index_bins = pd.cut(et_indices, bins=n_bins, labels=np.arange(n_bins))

    data_et = pd.DataFrame([], columns=['x', 'y', 't'])

    for index_bin in index_bins.unique():
        sub_index = et_indices[index_bins == index_bin]

        sub_data = pd.DataFrame([], columns=['x', 'y', 't'])

        for i in tqdm(sub_index, desc='Create eye-tracking data for bin ' +
                                      str(index_bin)):

            df = pd.read_json(data.loc[i, 'et_data'], orient='records')
            df["t_task"] = (df.loc[:, "t"] - df.loc[0, "t"])
            df[['run_id', 'trial_index']] = data.loc[i,
                                                     ['run_id', 'trial_index']]

            sub_data = sub_data.append(df)

        data_et = data_et.append(sub_data)

    return data_et


def create_et_data_1(data):
    data["et_data"] = data['et_data'].apply(str)

    df_et_data = data.loc[(pd.notna(data['et_data'])) &
                          ~(data['et_data'].isin(['"', '[]', 'nan'])),
                          ['run_id', 'trial_index', 'et_data']]

    text = '[' + '$'.join(df_et_data['et_data'].to_list()) + ']'
    my_list = json.loads(text.replace('$', ','))

    # b = []
    # for trial in my_list:
    #     a = []
    #     for line in trial:
    #         a.append(line.value())
    #     b.append(np.array(list(a)))

    et_data = [np.array([list(line.values()) for line in trial])
                         for trial in tqdm(my_list)]

    meta_data = df_et_data[['run_id', 'trial_index']]

    output = pd.DataFrame([])

    for meta, et in tqdm(zip(meta_data.values, et_data),
                         total=len(et_data),
                         desc='Append run and trial info to et-data: '):

        indices = np.full([len(et), len(meta)], meta)
        output = output.append(
            pd.DataFrame(np.concatenate([indices, et], axis=1)))

    output.columns = np.append(meta_data.columns.values, ['x', 'y', 't'])
    return output
