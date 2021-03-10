import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

from utils.path import makedir
from utils.plots import spaghetti_plot, save_plot


def add_trial_variables(data_trial):
    data_trial = invert_y_pos(data_trial)
    data_trial = add_window_size(data_trial)
    data_trial = exact_trial_duration(data_trial)
    data_trial = add_new_task_nr(data_trial)
    data_trial = add_trial_type_new(data_trial)
    data_trial = identify_fix_task(data_trial)
    data_trial = add_within_task_index(data_trial)
    data_trial = add_position_index(data_trial)

    return data_trial


def invert_y_pos(data_trial):
    data_trial['y_pos'] = 1 - data_trial['y_pos']

    return data_trial


def add_window_size(data):
    grouped = data.groupby(["run_id"], as_index=False)[[
        "window_width", "window_height"]].apply(max)

    grouped.columns = ["run_id", "window_width_max", "window_height_max"]

    grouped['window_diagonal_max'] = np.sqrt(
        grouped['window_width_max'] ** 2 + grouped['window_height_max'] ** 2)

    if "window_width_max" in data.columns:
        data = data.drop(columns=['window_width_max'])
    if "window_height_max" in data.columns:
        data = data.drop(columns=['window_height_max'])
    if "window_diagonal_max" in data.columns:
        data = data.drop(columns=['window_diagonal_max'])

    data = data.merge(grouped, on=['run_id'], how='left')

    data['window_diagonal'] = np.sqrt(
        data['window_width'] ** 2 + data['window_height'] ** 2)

    print(
        f"""data_trial: Added window height, width, and """
        f"""diagonal variables. \n"""
    )

    return data


def exact_trial_duration(data):
    data["t_startTrial"] = pd.concat(
        [pd.Series([0]), data["time_elapsed"]],
        ignore_index=True)
    data["trial_duration_exact"] = \
        data.loc[:, "time_elapsed"] - data.loc[:, "t_startTrial"]
    data.drop(len(data) - 1)

    print(f"""data_trial: Added trial_duration_exact: """)

    problematic_trials = check_time_deviation(
        data, 'rt', 'trial_duration_exact', 50)

    if len(problematic_trials) > 0:
        print(data.loc[
                  problematic_trials,
                  ['run_id', 'trial_index', 'trial_type',
                   'rt', 'trial_duration', 'trial_duration_exact']])

    problematic_trials = check_time_deviation(
        data, 'trial_duration', 'trial_duration_exact', 50)

    if len(problematic_trials) > 0:
        print(data.loc[
                  problematic_trials,
                  ['run_id', 'trial_index', 'trial_type',
                   'rt', 'trial_duration', 'trial_duration_exact']])

    return data


# noinspection PyUnnecessaryBackslash,PyTypeChecker
def check_time_deviation(data, column1, column2, max_time_diff_allowed):
    diff = data[column1] - data['trial_duration_exact']
    long_trials_run_id = data.loc[diff[diff > max_time_diff_allowed].index, 'run_id']
    long_trials_previous_run_id = pd.DataFrame(data.loc[diff[diff > max_time_diff_allowed].index - 1, 'run_id']) \
        .rename(columns={'run_id': 'previous_run_id'})
    long_trials_previous_run_id.index = long_trials_run_id.index
    compare_run_ids = pd.concat([long_trials_run_id, long_trials_previous_run_id], axis=1)

    problematic_trials = np.array([])

    if sum(compare_run_ids['run_id'] == \
           compare_run_ids['previous_run_id']) > 0:
        problematic_trials = compare_run_ids.loc[
                             (compare_run_ids['run_id'] == \
                              compare_run_ids['previous_run_id']), :].index

        print(
            f"""{column1}  and {column2} show a deviation of """
            f"""> {max_time_diff_allowed}  ms. """
            f"""Please check on the following indices: \n"""
            f"""{problematic_trials} \n""")

    else:
        print(
            f"""Success! {column1} and {column2} do not deviate """
            f"""by > {max_time_diff_allowed} ms. """
            f"""Will use trial_duration_exact in the future. \n""")

    return problematic_trials


def add_new_task_nr(data):
    data.loc[data['trial_index'] == 0, 'task_nr'] = 0
    data['task_nr_new'] = new_task_nr(data['task_nr'])
    data['task_nr_new'] = data['task_nr_new'].astype(int)

    print('data_trial: Add new task nr. \n')

    return data


# noinspection PyShadowingNames
def new_task_nr(task_nr):
    y = task_nr.copy()
    new_task_nr = 0

    for i in task_nr.index:
        x = task_nr[i]
        if pd.notna(x) & (x != '"'):
            new_task_nr = x
        else:
            y[i] = new_task_nr

    return y


def add_trial_type_new(data):
    """
        Most of these subjects reloaded when the eye-tracking initialized
        as well as during the first calibration

    """
    data['trial_type_new'] = 0

    data.loc[
        (data['run_id'] < 144) & (data['chinFirst'] == 0),
        'trial_type_new'
    ] = pd.cut(
        data.loc[
            (data['run_id'] < 144) & (data['chinFirst'] == 0),
            'trial_index'],
        np.array([
            0,
            1.5,  # start_page
            2.5,  # prolific_id
            4.5,  # pre_et_init
            5.5,  # et_init
            11,  # et_adjustment
            17.5,  # calibration_1_briefing
            18.5,  # first_cal
            97,  # calibration_1
            134,  # fixation_1
            221,  # calibration_2
            259,  # fixation_2
            514,  # choice
            520  # end
        ]),
        labels=np.array([
            'start_page',
            'prolific_id',
            'pre_et_init',
            'et_init',
            'et_adjustment',
            'calibration_1_briefing',
            'first_cal',
            'calibration_1',
            'fixation_1',
            'calibration_2',
            'fixation_2',
            'choice',
            'end'
        ]),
        include_lowest=True,
    )

    data.loc[
        (data['run_id'] < 144) & (data['chinFirst'] == 1),
        'trial_type_new'
    ] = pd.cut(
        data.loc[
            (data['run_id'] < 144) & (data['chinFirst'] == 1),
            'trial_index'],
        np.array([
            0,  #
            1.5,  # start_page
            2.5,  # prolific_id
            4.5,  # pre_et_init
            5.5,  # et_init
            11,  # et_adjustment
            17.5,  # calibration_1_briefing
            18.5,  # first_cal
            97,  # calibration_1
            134,  # fixation_1
            387,  # choice
            473,  # calibration_2
            513,  # fixation_2
            520  # end
        ]),
        labels=np.array([
            'start_page',
            'prolific_id',
            'pre_et_init',
            'et_init',
            'et_adjustment',
            'calibration_1_briefing',
            'first_cal',
            'calibration_1',
            'fixation_1',
            'choice',
            'calibration_2',
            'fixation_2',
            'end'
        ]),
        include_lowest=True,
    )

    data.loc[
        (data['run_id'] > 143) & (data['chinFirst'] == 0),
        'trial_type_new'
    ] = pd.cut(
        data.loc[
            (data['run_id'] > 143) & (data['chinFirst'] == 0),
            'trial_index'],
        np.array([
            0,
            1.5,  # start_page
            2.5,  # prolific_id
            4.5,  # pre_et_init
            5.5,  # et_init
            11,  # et_adjustment
            17.5,  # calibration_1_briefing
            97,  # calibration_1
            143,  # fixation_1
            231,  # calibration_2
            277,  # fixation_2
            532,  # choice
            540  # end
        ]),
        labels=np.array([
            'start_page',
            'prolific_id',
            'pre_et_init',
            'et_init',
            'et_adjustment',
            'calibration_1_briefing',
            'calibration_1',
            'fixation_1',
            'calibration_2',
            'fixation_2',
            'choice',
            'end'
        ]),
        include_lowest=True,
    )

    data.loc[
        (data['run_id'] > 143) & (data['chinFirst'] == 1),
        'trial_type_new'
    ] = pd.cut(
        data.loc[
            (data['run_id'] > 143) & (data['chinFirst'] == 1),
            'trial_index'],
        np.array([
            0,  #
            1.5,  # start_page
            2.5,  # prolific_id
            4.5,  # pre_et_init
            5.5,  # et_init
            11,  # et_adjustment
            17.5,  # calibration_1_briefing
            97,  # calibration_1
            143,  # fixation_1
            397,  # choice
            483,  # calibration_2
            532,  # fixation_2
            540  # end
        ]),
        labels=np.array([
            'start_page',
            'prolific_id',
            'pre_et_init',
            'et_init',
            'et_adjustment',
            'calibration_1_briefing',
            'calibration_1',
            'fixation_1',
            'choice',
            'calibration_2',
            'fixation_2',
            'end'
        ]),
        include_lowest=True,
    )

    data = order_trial_types(data)

    print('Added new trial_type_new (abstraction of trial_type)')

    return data


def order_trial_types(data_trial):
    types_and_numbers = pd.DataFrame(
        {'trial_type_new': [
            'start_page',
            'prolific_id',
            'pre_et_init',
            'et_init',
            'et_adjustment',
            'calibration_1_briefing',
            'calibration_1',
            'fixation_1',
            'calibration_2',
            'fixation_2',
            'choice',
            'end'
        ],
            'trial_type_nr': np.arange(12)
        }
    )

    if 'trial_type_nr' in data_trial.columns:
        data_trial = data_trial.drop(columns='trial_type_nr')

    data_trial = data_trial \
        .merge(types_and_numbers, on='trial_type_new', how='left')

    return data_trial


def identify_fix_task(data_trial):
    data_trial['fixTask'] = 0

    data_trial.loc[
        (data_trial['trial_type'] == 'eyetracking-fix-object') &
        (data_trial['trial_duration'] == 5000),
        'fixTask'
    ] = 1

    print('data_trial: Added fixation task. \n')

    return data_trial


def add_within_task_index(data):
    new_indices = within_task_index(data)
    if 'withinTaskIndex' in data.columns:
        data = data.drop(columns=['withinTaskIndex'])
    data = data.merge(
        new_indices,
        on=['run_id', 'trial_index'],
        how='left')

    example = data.loc[
        (data['run_id'] == data['run_id'].unique()[0]) &
        (data['fixTask'] == 1),
        ['run_id', 'trial_index', 'withinTaskIndex', 'trial_type']
    ].head(5)

    print(
        f"""Added withinTaskIndex: \n"""
        f"""{example} \n"""
    )

    return data


def within_task_index(data):
    all_trial_indices = []
    for subject in tqdm(
            data["run_id"].unique(),
            desc='Calculate withinTaskIndex'):
        df_subj = data.loc[data['run_id'] == subject, :]

        for trial_type in df_subj['trial_type'].unique():
            df_trial = df_subj.loc[df_subj['trial_type'] == trial_type, :]

            for task_nr in df_trial["task_nr"].unique():
                df_task = df_trial.loc[df_trial['task_nr'] == task_nr, :]

                for fixTask in df_task['fixTask'].unique():
                    df_fix_task = df_task.loc[
                        df_task['fixTask'] == fixTask,
                        ['run_id', 'trial_index']] \
                        .drop_duplicates() \
                        .reset_index(drop=True)

                    df_fix_task['withinTaskIndex'] = df_fix_task.index + 1
                    all_trial_indices.append(df_fix_task)
    all_trial_indices = pd.concat(all_trial_indices).reset_index(drop=True)
    return all_trial_indices


def add_position_index(data):
    data['positionIndex'] = 0

    x_pos = [0.2, 0.5, 0.8, 0.2, 0.5, 0.8, 0.2, 0.5, 0.8, 0.35, 0.65, 0.35, 0.65]
    y_pos = [0.2, 0.2, 0.2, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8, 0.35, 0.35, 0.65, 0.65]

    for i in range(0, len(x_pos)):
        data.loc[(data['x_pos'] == x_pos[i]) & (data['y_pos'] == y_pos[i]), 'positionIndex'] = i

    grouped_position_indices = data.loc[
        (data['trial_type'] == 'eyetracking-calibration'), ['x_pos', 'y_pos', 'positionIndex']] \
        .drop_duplicates() \
        .sort_values(by='positionIndex')

    print(f'Added position index: \n {grouped_position_indices} \n')

    return data


def add_fps_trial_level(data_trial, data_et):
    data_trial = merge_count_by_index(data_trial, data_et, 'x')

    data_trial['fps'] = \
        1000 * data_trial['x_count'] / \
        data_trial['trial_duration_exact']

    plot_fps_over_trials(data_trial)

    return data_trial


def merge_count_by_index(data, large_data, var_name):
    if var_name + '_count' in data.columns:
        data = data.drop(columns=[var_name + '_count'])
    grouped = large_data.groupby(["run_id", "trial_index"])[var_name].count() \
        .reset_index() \
        .rename(columns={var_name: var_name + '_count'})
    data = data.merge(grouped, on=["run_id", "trial_index"], how='left')

    return data


def plot_fps_over_trials(data_trial):
    spaghetti_plot(
        data_trial.loc[(data_trial['chinFirst'] == 0) & pd.notna(data_trial['fps']), :],
        'trial_index', 'fps', 103)
    plt.title('chinFirst == 0', loc='center', fontsize=12, fontweight=0, color='grey')
    plt.xlabel('trial_index')
    plt.ylabel('fps')
    plt.vlines(18, 45, 50, colors='k', linestyles='solid')
    plt.text(18 + 1, 50, s='Calibration')
    plt.vlines(105, 45, 50, colors='k', linestyles='solid')
    plt.text(105 + 1, 50, s='fix Task')
    plt.vlines(143, 45, 50, colors='k', linestyles='solid')
    plt.text(143 + 1, 50, s='Calibration')
    plt.vlines(230, 45, 50, colors='k', linestyles='solid')
    plt.text(230 + 1, 50, s='fix Task')
    plt.vlines(269, 45, 50, colors='k', linestyles='solid')
    plt.text(269 + 1, 50, s='choice Task')

    save_plot('results', 'plots', 'fps', 'chin_first_0.png')

    spaghetti_plot(
        data_trial.loc[(data_trial['chinFirst'] == 1) & pd.notna(data_trial['fps']), :],
        'trial_index', 'fps', 91)
    plt.title('chinFirst == 1', loc='center', fontsize=12, fontweight=0, color='grey')
    plt.xlabel('trial_index')
    plt.ylabel('fps')
    plt.vlines(18, 45, 50, colors='k', linestyles='solid')
    plt.text(18 + 1, 50, s='Calibration')
    plt.vlines(105, 45, 50, colors='k', linestyles='solid')
    plt.text(105 + 1, 50, s='fix Task')
    plt.vlines(144, 45, 50, colors='k', linestyles='solid')
    plt.text(144 + 1, 50, s='choice Task')
    plt.vlines(394, 45, 50, colors='k', linestyles='solid')
    plt.text(394 + 1, 50, s='Calibration')
    plt.vlines(482, 45, 50, colors='k', linestyles='solid')
    plt.text(482 + 1, 50, s='fix Task')

    save_plot('results', 'plots', 'fps', 'chin_first_1.png')

