def reformat_yang(text):
    text = text.replace('$', ',')
    text = text.replace("relative-x", "x")
    text = text.replace("relative-y", 'y')
    text = text.replace('elapse-time', 't')
    text = (text[11:len(text)-1])
    return(text)

def reformat_yang_data(data_raw):

    for subject in data_yang['run_id'].unique():
       for i in data_raw.loc[
           (data_raw['run_id']==subject) &
           (pd.notna(data_raw['et_data'])) &
           ~(data_raw['et_data'].isin(['"', 'nan'])),
          :].index:
          print('Reformat index: ' + str(i))
          data_raw.loc[i, 'et_data'] = reformatYang(data_raw.loc[i, 'et_data'])

    return data_raw