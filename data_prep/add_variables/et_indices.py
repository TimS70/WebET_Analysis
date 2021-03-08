import numpy as np
import pandas as pd


def add_et_indices(data_trial, data_et):
    data_trial['optionIndex'] = addOptionIndex(data_trial)
    data_trial['attributeIndex'] = addAttributeIndex(data_trial)

    data_trial = addTransition_type(data_trial, data_et)
    data_trial['payneIndex'] = addPayneIndex(data_trial)

    return data_trial


def addOptionIndex(data):
    gazePoints_immediate = \
        require_min(data['aoi_aSS'], 3) + \
        require_min(data['aoi_tSS'], 3)
    gazePoints_delay = \
        require_min(data['aoi_aLL'], 3) + \
        require_min(data['aoi_tLL'], 3)
    optionIndex = \
        (gazePoints_immediate - gazePoints_delay) / \
        (gazePoints_immediate + gazePoints_delay)

    overview = pd.DataFrame(
        [
            [sum(pd.isna(optionIndex))],
            [sum(optionIndex == 1)],
            [sum(optionIndex == 0)],
            [sum((optionIndex > 0) &
                 (optionIndex < 1))],
            [len(optionIndex)]
        ],
        index=['NAN', '1', '0', '0>optionIndex>1', 'total'],
        columns=['n_trials']
    )

    print(
        f"""data_trial: Added Option Index: \n"""
        f"""{optionIndex.describe()} \n"""
        f"""{overview} \n"""
    )

    return optionIndex


def require_min(data, min_required_count):
    return data.replace(
        np.arange(min_required_count),
        np.repeat(0, min_required_count))


def addAttributeIndex(data):
    gazePoints_amount = \
        require_min(data['aoi_aLL'], 3) + \
        require_min(data['aoi_aSS'], 3)
    gazePoints_time = \
        require_min(data['aoi_tLL'], 3) + \
        require_min(data['aoi_tSS'], 3)

    attributeIndex = \
        (gazePoints_amount - gazePoints_time) / \
        (gazePoints_amount + gazePoints_time)

    overview = pd.DataFrame(
        [
            [sum(pd.isna(attributeIndex))],
            [sum(attributeIndex == 1)],
            [sum(attributeIndex == 0)],
            [sum((attributeIndex > 0) &
                 (attributeIndex < 1))],
            [len(attributeIndex)]
        ], index=['NAN', '1', '0', '0>attributeIndex>1', 'total'],
        columns=['n_trials']
    )

    print(
        f"""data_trial: Added Attribute Index: \n"""
        f"""{attributeIndex.describe()} \n"""
        f"""{overview} \n"""
    )

    return attributeIndex


def et_data_transition_type(data):
    data = data.loc[
           pd.notna(data['aoi']) &
           (data['aoi'] != 0), :].copy()

    data['newAOIIndex'] = 0
    data.loc[(data['aoi_aLL'] == 1), 'newAOIIndex'] = 1
    data.loc[(data['aoi_tLL'] == 1), 'newAOIIndex'] = 2
    data.loc[(data['aoi_aSS'] == 1), 'newAOIIndex'] = 4
    data.loc[(data['aoi_tSS'] == 1), 'newAOIIndex'] = 8
    data.sort_values(by=['run_id', 'withinTaskIndex'])
    # Add a 0 due to the way np.diff works
    data['transition_type'] = np.append([0], np.diff(data['newAOIIndex']))
    data['transition_type'] = abs(data['transition_type'])

    data.loc[data['t_task'] == 0, 'transition_type'] = 0

    return data.loc[:, ['run_id', 'trial_index', 't_task', 'transition_type']]


def addTransition_type(data, data_et):
    data_et = et_data_transition_type(data_et)
    data_et.loc[:, 'transition_type'] = data_et.loc[:, 'transition_type']

    transition_count = pd.pivot_table(
        data_et.loc[:, ['run_id', 'trial_index', 'transition_type']],
        index=['run_id', 'trial_index'],
        columns=['transition_type'],
        aggfunc=len,
        fill_value=0) \
        .reset_index() \
        .rename(columns={
        0: "trans_type_0",
        1: "trans_type_aLLtLL",
        2: "trans_type_tLLaSS",
        3: "trans_type_aLLaSS",
        4: "trans_type_aSStSS",
        6: "trans_type_tLLtSS",
        7: "trans_type_aLLtSS",
        8: "trans_type_0_tSS",
    })

    transition_columns = ["trans_type_0", "trans_type_aLLtLL",
                          "trans_type_tLLaSS", "trans_type_aLLaSS",
                          "trans_type_aSStSS", "trans_type_tLLtSS",
                          "trans_type_aLLtSS"]

    for var in transition_columns:
        if var in data:
            data = data.drop(columns=[var])

    data = data.merge(transition_count, on=['run_id', 'trial_index'], how='left')
    data.loc[:, transition_columns] = data.loc[:, transition_columns] \
        .fillna(0)

    return data


def addPayneIndex(data):
    optionWise_transition = \
        data['trans_type_aLLtLL'] + \
        data['trans_type_aSStSS']
    attributeWise_transition = \
        data['trans_type_aLLaSS'] + \
        data['trans_type_tLLtSS']

    payneIndex = \
        (optionWise_transition - attributeWise_transition) / \
        (optionWise_transition + attributeWise_transition)


    overview = pd.DataFrame(
        [
            [sum(pd.isna(payneIndex))],
            [sum(payneIndex == 1)],
            [sum(payneIndex == 0)],
            [sum((payneIndex > 0) &
                 (payneIndex < 1))],
            [len(payneIndex)]
        ], index=['NAN', '1', '0', '0>attributeIndex>1', 'total'],
        columns=['n_trials']
    )

    print(
        f"""data_trial: Added option index: \n"""
        f"""{payneIndex.describe()} \n"""
        f"""{overview} \n"""
    )

    return payneIndex
