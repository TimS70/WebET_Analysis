import numpy as np
import pandas as pd


def add_subject_variables(data_subject, data_trial):
    data_subject = add_fps_subject_level(data_subject, data_trial)
    data_subject = add_max_trials(data_subject, data_trial)
    data_subject = add_glasses_binary(data_subject)
    data_subject = add_completed_date(data_subject, data_trial)
    data_subject = add_employment_status(data_subject)
    data_subject = add_full_time_binary(data_subject)

    data_subject.to_csv(
        "data/added_var/data_subject.csv",
        index=False, header=True)

    return data_subject


def add_fps_subject_level(data_subject, data_trial):
    data_subject = merge_by_subject(data_subject, data_trial, 'fps')
    plt.hist(data_subject['fps'], bins=15)
    plt.savefig('plots/fps/chin_first_0.png')

    return data_subject


def add_max_trials(data_subject, data_trial):
    data_subject = data_subject \
        .merge(
            data_trial.groupby(['run_id'], as_index=False)['trial_index'].max(),
            on=['run_id'],
            how='left') \
        .rename(columns={'trial_index': 'max_trial'})

    return data_subject


def add_glasses_binary(data_subject):
    data_subject['glasses_binary'] = data_subject['sight'] \
        .replace({'contactLenses': 0,
                  'glasses': 1,
                  'notCorrected': 0,
                  'perfectSight': 0}
                 )
    print(f"""Unique values glasses_binary: {data_subject['glasses_binary'].unique()}""")

    return data_subject


def add_completed_date(data_subject, data_trial):
    output = []

    for subject in tqdm(data_trial['run_id'].unique()):
        this_subject = data_trial.loc[data_trial['run_id'] == subject] \
            .reset_index(drop=True)
        date_time_obj = datetime.datetime.strptime(
            this_subject.loc[0, 'recorded_at'], '%Y-%m-%d %H:%M:%S')

        output.append([this_subject.loc[0, 'run_id'], date_time_obj.date()])

    output = pd.DataFrame(output, columns=['run_id', 'recorded_date'])

    if 'recorded_date' in data_subject.columns:
        data_subject = data_subject.drop(columns=['recorded_date'])

    data_subject = data_subject.merge(output, on='run_id', how='left')

    return data_subject


def add_employment_status(data_subject):
    data_subject['employment_status'] = data_subject['Employment Status'].replace({
        """Not in paid work (e.g. homemaker', 'retired or disabled)""": 'not_in_paid_work',
        'DATA EXPIRED': 'Other',
        'Unemployed (and job seeking)': 'not_in_paid_work',
        'Due to start a new job within the next month': 'Other'
    })

    return data_subject


def add_full_time_binary(data_subject):
    data_subject['fullTime_binary'] = data_subject['Employment Status'].replace({
        'Other': 0,
        'Full-Time': 1,
        'Part-Time': 0,
        "Not in paid work (e.g. homemaker', 'retired or disabled)": 0,
        'Unemployed (and job seeking)': 0,
        'DATA EXPIRED': 0
    })

    return data_subject
