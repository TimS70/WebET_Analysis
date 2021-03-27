import numpy as np


def identify_amount_left(data):
    data['amountLeft'] = 0
    data.loc[
        (data['option_topLeft'].str.contains("\$", regex=True)) |
        (data['option_topLeft'].str.contains("cent", regex=True)),
        'amountLeft'] = 1
    data['amountLeft'].unique()

    grouped_test = data.groupby(
        ['run_id', 'amountLeft'],
        as_index=False).agg(
        n=('trial_index', 'count'),
        max_task_nr=('withinTaskIndex', 'max'),
        min_task_nr=('withinTaskIndex', 'min'),
    )

    example = data.loc[:,
             ['amountLeft', 'option_topLeft', 'option_bottomLeft',
              'option_topRight', 'option_bottomRight']] \
        .sort_values(by='amountLeft')

    print(
        f"""data_trial: Identify amount left: \n"""
        f"""{example} \n"""
        f"""{grouped_test} \n"""
    )
    return data


def add_choice_options_num(data_trial):
    data_trial = data_trial \
        .rename(columns={
            'option_topLeft': 'option_TL',
            'option_bottomLeft': 'option_BL',
            'option_topRight': 'option_TR',
            'option_bottomRight': 'option_BR'})

    variables = [
        'option_TL',
        'option_BL',
        'option_TR',
        'option_BR'
    ]
    for var in variables:
        data_trial = choice_options_to_numeric(data_trial, var)

    print(f"""data_trial: Add choice_options_num. \n""")

    return data_trial


def choice_options_to_numeric(data, var_name):
    data[var_name + '_num'] = data[var_name]
    data[var_name + '_num'] = data[var_name + '_num'] \
        .replace(['Today', 'Tomorrow', '7 days',
                  '15 days', '30 days', '90 days',
                  '180 days'],
                 [0, 1, 7, 15, 30, 90, 180]) \
        .replace({'\$': ''}, regex=True) \
        .replace('50 cent', 0.5) \
        .astype(float)

    return data


def reformat_attributes(data):
    data['aSS'] = 0
    data.loc[data['amountLeft'] == 1, 'aSS'] = \
        data.loc[
            data['amountLeft'] == 1,
            ["option_TL_num", "option_BL_num"]
        ].values.min(1)
    data.loc[data['amountLeft'] == 0, 'aSS'] = \
        data.loc[
            data['amountLeft'] == 0,
            ["option_TR_num", "option_BR_num"]
        ].values.min(1)

    data['aLL'] = 0
    data.loc[data['amountLeft'] == 1, 'aLL'] = \
        data.loc[
            data['amountLeft'] == 1,
            ["option_TL_num", "option_BL_num"]
        ].values.max(1)
    data.loc[data['amountLeft'] == 0, 'aLL'] = \
        data.loc[
            data['amountLeft'] == 0,
            ["option_TR_num", "option_BR_num"]
        ].values.max(1)

    data.loc[:, "tSS"] = 0

    data['tLL'] = 0
    data.loc[data['amountLeft'] == 1, 'tLL'] = \
        data.loc[
            data['amountLeft'] == 1,
            ["option_TR_num", "option_BR_num"]
        ].values.max(1)
    data.loc[data['amountLeft'] == 0, 'tLL'] = \
        data.loc[
            data['amountLeft'] == 0,
            ["option_TL_num", "option_BL_num"]
        ].values.max(1)

    # noinspection PyUnresolvedReferences
    data['LL_top'] = (data["option_TL_num"] > data["option_BL_num"]).astype(int)

    print('data_trial: Identified information attributes: ')
    print('aLL values: ' + str(np.sort(data['aLL'].unique())))
    print('aSS values: ' + str(np.sort(data['aSS'].unique())))
    print('tLL values: ' + str(np.sort(data['tLL'].unique())))
    print('tSS values: ' + str(np.sort(data['tSS'].unique())) + '\n')

    return data


def top_bottom_attributes(data):
    data['aT'] = data['LL_top'] * data['aLL'] + \
        (1-data['LL_top']) * data['aSS']
    data['aB'] = (1-data['LL_top']) * data['aLL'] + \
        data['LL_top'] * data['aSS']
    data['tT'] = data['LL_top'] * data['tLL'] + \
        (1-data['LL_top']) * data['tSS']
    data['tB'] = (1-data['LL_top']) * data['tLL'] + \
        data['LL_top'] * data['tSS']

    example = data.loc[
        :,
        ['aT', 'tT', 'aB', 'tB', 'LL_top']
    ].sort_values(by='LL_top')

    grouped_test = data.groupby(
        ['run_id', 'LL_top'],
        as_index=False).agg(
            n=('trial_index', 'count'),
            max_trial=('withinTaskIndex', 'max'),
            aT_min=('aT', 'min'),
            aT_max=('aT', 'max'),
            aB_min=('aB', 'min'),
            aB_max=('aB', 'max'),
    )

    print(
        f"""data_trial: Added top and bottom attributes: \n"""
        f"""{example} \n"""
        f"""{grouped_test} \n""")

    return data


def add_k(a_ll, a_ss, t_ll):
    return ((a_ll / a_ss) - 1) / t_ll


