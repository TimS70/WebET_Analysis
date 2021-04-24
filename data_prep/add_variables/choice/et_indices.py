import numpy as np
import pandas as pd

from utils.combine import merge_by_index


def add_et_indices(data_trial, data_et, min_gaze_points=3):

    data_trial['optionIndex'] = add_option_index(data_trial, min_gaze_points)
    data_trial['attributeIndex'] = add_attribute_index(data_trial,
                                                       min_gaze_points)

    print(data_trial[['aoi_aLL', 'aoi_tLL', 'aoi_aSS', 'aoi_tSS',
                     'attributeIndex', 'optionIndex']].head(10))

    data_trial = add_transition_type(data_trial, data_et)
    data_trial['payneIndex'] = add_payne_index(data_trial)

    print(f"""Eye-tracking Indices: \n"""
          f"""{data_trial[['attributeIndex', 'optionIndex', 
                           'payneIndex']].describe()}""")
    return data_trial


def add_option_index(data, min_n_points):
    gaze_points_immediate = \
        require_min_gaze_points(data['aoi_aSS'], min_n_points) + \
        require_min_gaze_points(data['aoi_tSS'], min_n_points)

    gaze_points_delay = \
        require_min_gaze_points(data['aoi_aLL'], min_n_points) + \
        require_min_gaze_points(data['aoi_tLL'], min_n_points)
    option_index = \
        (gaze_points_immediate - gaze_points_delay) / \
        (gaze_points_immediate + gaze_points_delay)

    overview = et_var_overview(option_index)

    print(
        f"""data_trial: Added Option Index with a minimum """
        f"""required number of {min_n_points} gaze points in an AOI: \n"""
        f"""{option_index.describe()} \n"""
        f"""{overview} \n"""
    )

    return option_index


def require_min_gaze_points(data, min_required_count):
    return data.replace(
        np.arange(min_required_count),
        np.repeat(0, min_required_count))


def add_attribute_index(data, min_n_points):
    gaze_points_amount = \
        require_min_gaze_points(data['aoi_aLL'], min_n_points) + \
        require_min_gaze_points(data['aoi_aSS'], min_n_points)
    gaze_points_time = \
        require_min_gaze_points(data['aoi_tLL'], min_n_points) + \
        require_min_gaze_points(data['aoi_tSS'], min_n_points)

    attribute_index = \
        (gaze_points_amount - gaze_points_time) / \
        (gaze_points_amount + gaze_points_time)

    overview = et_var_overview(attribute_index)

    print(
        f"""data_trial: Added Attribute Index with a minimum """
        f"""required number of {min_n_points} gaze points in an AOI: \n"""
        f"""{attribute_index.describe()} \n"""
        f"""{overview} \n"""
    )

    return attribute_index


def et_data_transition_type(data):
    data = data[pd.notna(data['aoi']) & (data['aoi'] != 0)].copy()

    data['newAOIIndex'] = 0
    data.loc[(data['aoi_aLL'] == 1), 'newAOIIndex'] = 1
    data.loc[(data['aoi_tLL'] == 1), 'newAOIIndex'] = 2
    data.loc[(data['aoi_aSS'] == 1), 'newAOIIndex'] = 4
    data.loc[(data['aoi_tSS'] == 1), 'newAOIIndex'] = 8
    data.sort_values(by=['run_id', 'withinTaskIndex'])
    # Add a 0 due to the way np.diff works
    data['transition_type'] = np.append([0], np.diff(data['newAOIIndex']))

    if 't_task' in data.columns:
        data.loc[data['t_task'] == 0, 'transition_type'] = 0
        data = data[['run_id', 'trial_index', 't_task', 'transition_type']]
    else:
        new_trial_begins = (np.append([0], np.diff(data['trial_index'])) != 0) \
            .astype(int)

        data = data.reset_index(drop=True)

        data.loc[new_trial_begins, 'transition_type'] = 0
        data = data[['run_id', 'trial_index', 'transition_type']]

    return data


def add_transition_type(data, data_et):
    data_et = et_data_transition_type(data_et)
    data_et['transition_type'] = data_et['transition_type']

    transition_count = pd.pivot_table(
        data_et[['run_id', 'trial_index', 'transition_type']],
        index=['run_id', 'trial_index'],
        columns=['transition_type'],
        aggfunc=len,
        fill_value=0) \
        .reset_index() \
        .rename(columns={0: "trans_type_0",
                         1: "trans_type_aLLtLL",
                         2: "trans_type_tLLaSS",
                         3: "trans_type_aLLaSS",
                         4: "trans_type_aSStSS",
                         6: "trans_type_tLLtSS",
                         7: "trans_type_aLLtSS",
                         -1: "trans_type_tLLaLL",
                         -2: "trans_type_aSStLL",
                         -3: "trans_type_aSSaLL",
                         -4: "trans_type_tSSaSS",
                         -6: "trans_type_tSStLL",
                         -7: "trans_type_tSSaLL"})

    transition_columns = transition_count \
        .drop(columns=['run_id', 'trial_index']) \
        .columns

    for col in transition_columns:
        data = merge_by_index(data, transition_count, col)

    data[transition_columns] = data[transition_columns].fillna(0)

    return data


def add_payne_index(data):
    option_wise_transition = \
        data['trans_type_aLLtLL'] + data['trans_type_tLLaLL'] + \
        data['trans_type_aSStSS'] + data['trans_type_tSSaSS']
    attribute_wise_transition = \
        data['trans_type_aLLaSS'] + data['trans_type_aSSaLL'] + \
        data['trans_type_tLLtSS'] + data['trans_type_tSStLL']

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
