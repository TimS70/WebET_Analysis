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


def text_to_data_frame(text):
    text = text.replace('$', ',')
    dataframe = pd.read_json(text, orient='records')
    return dataframe


def create_et_data(data):
    data["et_data"] = data['et_data'].apply(str).replace('$', ',')

    df_et_data = data.loc[(pd.notna(data['et_data'])) &
                          ~(data['et_data'].isin(['"', '[]', 'nan'])),
                          ['run_id', 'trial_index', 'et_data']]

    my_list = json.loads('[' + ','.join(df_et_data['et_data'].to_list()) + ']')

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
    print(output)
    print(output['run_id'].unique())
    exit()
    return output
