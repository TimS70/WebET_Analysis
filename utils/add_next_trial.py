import numpy as np


def add_next_trial(data, data_trial):
    full_trials_no_chin = data_trial.loc[
        data_trial['run_id'] == 421,
        ['trial_index', 'trial_type', 'trial_type_new']
    ].reset_index(drop=True)

    next_trials_no_chin = full_trials_no_chin
    next_trials_no_chin['trial_index'] -= 1

    full_trials_chin = data_trial.loc[
        data_trial['run_id'] == 270,
        ['trial_index', 'trial_type', 'trial_type_new']
    ].reset_index(drop=True)

    next_trials_chin = full_trials_chin
    next_trials_chin['trial_index'] -= 1

    data = data.copy()
    data['next_trial_type'] = 0
    data['next_trial_type_new'] = 0

    for i in data.index:
        this_trial = data.loc[i, 'trial_index']

        if data.loc[i, 'trial_type_new'] != 'end':
            if this_trial > 0:
                next_trials = next_trials_chin \
                    if data.loc[i, 'chinFirst'] > 0 \
                    else next_trials_no_chin

                next_trial_type = next_trials.loc[
                    next_trials['trial_index'] == this_trial,
                    'trial_type'].values[0]

                next_trial_type_new = next_trials.loc[
                    next_trials['trial_index'] == this_trial,
                    'trial_type_new'].values[0]

            else:
                next_trial_type = np.nan
                next_trial_type_new = np.nan

            data.loc[i, 'next_trial_type'] = next_trial_type
            data.loc[i, 'next_trial_type_new'] = next_trial_type_new

        else:
            data.loc[i, 'next_trial_type'] = 'end'
            data.loc[i, 'next_trial_type_new'] = 'end'

    return data