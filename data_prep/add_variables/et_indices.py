import numpy as np
import pandas as pd


def add_et_indices(data_trial, data_et):
    data_trial['optionIndex'] = add_option_index(data_trial)
    data_trial['attributeIndex'] = add_attribute_index(data_trial)

    data_trial = add_transition_type(data_trial, data_et)
    data_trial['payneIndex'] = add_payne_index(data_trial)

    return data_trial


def add_option_index(data):
    gaze_points_immediate = \
        require_min(data['aoi_aSS'], 3) + \
        require_min(data['aoi_tSS'], 3)
    gaze_points_delay = \
        require_min(data['aoi_aLL'], 3) + \
        require_min(data['aoi_tLL'], 3)
    option_index = \
        (gaze_points_immediate - gaze_points_delay) / \
        (gaze_points_immediate + gaze_points_delay)

    overview = et_var_overview(option_index)

    print(
        f"""data_trial: Added Option Index: \n"""
        f"""{option_index.describe()} \n"""
        f"""{overview} \n"""
    )

    return option_index


def require_min(data, min_required_count):
    return data.replace(
        np.arange(min_required_count),
        np.repeat(0, min_required_count))


def add_attribute_index(data):
    gaze_points_amount = \
        require_min(data['aoi_aLL'], 3) + \
        require_min(data['aoi_aSS'], 3)
    gaze_points_time = \
        require_min(data['aoi_tLL'], 3) + \
        require_min(data['aoi_tSS'], 3)

    attribute_index = \
        (gaze_points_amount - gaze_points_time) / \
        (gaze_points_amount + gaze_points_time)

    overview = et_var_overview(attribute_index)

    print(
        f"""data_trial: Added Attribute Index: \n"""
        f"""{attribute_index.describe()} \n"""
        f"""{overview} \n"""
    )

    return attribute_index


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


def add_transition_type(data, data_et):
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
            8: "trans_type_0_tSS"})

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


def add_payne_index(data):
    option_wise_transition = \
        data['trans_type_aLLtLL'] + \
        data['trans_type_aSStSS']
    attribute_wise_transition = \
        data['trans_type_aLLaSS'] + \
        data['trans_type_tLLtSS']

    payne_index = \
        (option_wise_transition - attribute_wise_transition) / \
        (option_wise_transition + attribute_wise_transition)

    overview = et_var_overview(payne_index)

    print(
        f"""data_trial: Added option index: \n"""
        f"""{payne_index.describe()} \n"""
        f"""{overview} \n"""
    )

    return payne_index


def et_var_overview(et_index):
    overview = pd.DataFrame(
        [
            [sum(pd.isna(et_index))],
            [sum(et_index == 1)],
            [sum(et_index == 0)],
            [sum((et_index > 0) &
                 (et_index < 1))],
            [len(et_index)]
        ], index=['NAN', '1', '0', '0>ET-Index>1', 'total'],
        columns=['n_trials'])

    return overview