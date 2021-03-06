def textToDataframe(text):
    text = text.replace('$', ',')
    dataframe = pd.read_json(text, orient='records')
    return (dataframe)


def extract_et_data(data):
    data_eyetracking = pd.DataFrame(columns=['x', 'y', 't'])
    data["et_data"] = data['et_data'].apply(str)

    et_indices = data.loc[
                 (pd.notna(data['et_data'])) &
                 ~(data['et_data'].isin(['"', '[]', 'nan'])),
                 :].index
    index_max = et_indices.max()

    for i in tqdm(et_indices):
        df = textToDataframe(data.loc[i, 'et_data'])

        df["t_task"] = (df.loc[:, "t"] - df.loc[0, "t"])
        df['run_id'] = data.loc[i, 'run_id']
        df['trial_index'] = data.loc[i, 'trial_index']

        data_eyetracking = data_eyetracking.append(pd.DataFrame(data=df), ignore_index=True)

    if not os.path.exists('./data_jupyter/raw'):
        os.mkdir('./data_jupyter/raw')

    data_et.to_csv("data_jupyter/raw/data_et.csv", index=False, header=True)
    print('data_et saved!')

    return data_eyetracking