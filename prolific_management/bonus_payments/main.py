import datetime
import pandas as pd
import os

print("Current Working directory: ", os.getcwd())


def load_data():
    data_prolific_int = pd.read_csv(r'input_data/prolific_export_int.csv') \
        .rename(columns={'participant_id': 'prolificID'})

    data_prolific_us = pd.read_csv(r'input_data/prolific_export_us.csv') \
        .rename(columns={'participant_id': 'prolificID'})

    data_subject = pd.read_csv(r'input_data/data_subject_raw.csv') \
        .loc[
                   :,
                   ['run_id', 'prolificID', 'recorded_date',
                    'birthyear', 'webcam_fps', 'webcam_label',
                    'chosenAmount', 'chosenDelay']] \
        .drop_duplicates() \
        .rename(columns={'chosenAmount': 'bonus_USD',
                         'chosenDelay': 'bonus_delay'})
    data_subject['prolificID'] = data_subject['prolificID'].str.strip()

    data = data_prolific_int \
        .append(data_prolific_us) \
        .merge(data_subject,
               on='prolificID',
               how='left')
    print(f'Number of datasets: {len(data)}')
    return data


data_prolific = load_data()


def filter_data(data):
    data = data.loc[
        data['status'] == 'APPROVED',
        [
            'run_id', 'prolificID',
            'age', 'Country of Birth', 'Current Country of Residence', 'First Language',
            'Nationality', 'Sex',
            'status', 'reviewed_at_datetime', 'Country of Birth', 'entered_code',
            'session_id', 'started_datetime', 'completed_date_time', 'time_taken',
            'bonus_USD', 'bonus_delay'
        ]
    ]
    print(f'Number of approved subjects: {len(data)}')
    return data


data_pay = filter_data(data_prolific)


def reformat_payments(data):
    data['bonus_delay'] = data['bonus_delay'].astype(str)
    data['bonus_delay'] = data['bonus_delay'] \
        .replace(['Today', 'Tomorrow', '7 days',
                  '15 days', '30 days', '90 days',
                  '180 days'],
                 [0, 1, 7, 15, 30, 90, 180]) \
        .astype(float)

    data['bonus_USD'] = data['bonus_USD'].astype(str)
    data['bonus_USD'] = data['bonus_USD'] \
        .replace({'\$': ''}, regex=True) \
        .replace('50 cent', 0.5) \
        .astype(float)
    return data


data_pay = reformat_payments(data_pay)


def insert_missing_values(data):
    data.loc[
        data['prolificID'].isin([
            '5ef6d07be683903cd5ae171d',
            '5fea6632bf9ae4a79153efdf',
            '60186dc2cc1aa8103499603a',
            '5f4fe72e9468441227166179',
            '5ec5a64c306f255ec98d5cc1',
            '5b8969006651ea000118e42e',
            '5fb2af792942a58ffe303948',
            '5edc20443467e28ec4e30f93',
            '5fa1192cf99e161a5cfad1cd',
            '5d430fdf871f1700017b2a81',
            '5c95970cd676900016e1a940',
        ]), ['bonus_USD', 'bonus_delay']] = [5, 1]

    bonus_nan = data.loc[
        data[['bonus_USD', 'bonus_delay']].isnull().any(axis=1),
        ['run_id', 'prolificID', 'started_datetime', 'reviewed_at_datetime']
    ]

    if len(bonus_nan) > 0:
        print(f'There are missing values in bonus payment: '
              f'Check out the following: \n {bonus_nan}')
    else:
        print('Success: No missing data for bonus nan')

    return data


data_pay = insert_missing_values(data_pay)


def add_currencies(data):
    data['bonus_GBP'] = data['bonus_USD'] * 0.75
    data['bonus_EUR'] = data['bonus_GBP'] * 1.13
    return data


data_pay = add_currencies(data_pay)


def add_variable_due_on(data):
    data.loc[data['run_id'] == 444, 'completed_date_time'] = \
        '2021-02-13 21:52:30.000000'

    data['completed_date'] = data.apply(
        lambda x: datetime.datetime.strptime(
            x['completed_date_time'], '%Y-%m-%d %H:%M:%S.%f').date(),
        axis=1)

    data['due_on'] = data['completed_date'] + data['bonus_delay'].map(datetime.timedelta)
    return data


data_pay = add_variable_due_on(data_pay)


def save_data_bonus_due_on(data):
    data \
        .loc[
            :,
            [
                'prolificID', 'run_id',
                'Nationality', 'Current Country of Residence', 'Sex',
                'bonus_USD', 'bonus_GBP', 'bonus_EUR',
                'completed_date', 'bonus_delay', 'due_on'
            ]
            ] \
        .sort_values(by='due_on') \
        .to_csv(
            'output_data/bonus_due_on.csv',
            index=False,
            header=False
        )


save_data_bonus_due_on(data_pay)


def save_data_bonus_due_today(data):
    bonus_due_today = data.loc[
        (data['due_on'] == datetime.datetime.now().date()),
        ['run_id', 'prolificID', 'status',
         'started_datetime', 'reviewed_at_datetime',
         'bonus_GBP', 'bonus_delay', 'due_on']
    ].sort_values(by='due_on')

    bonus_due_today['bonus_GBP'] = bonus_due_today['bonus_GBP'].round(2)

    if not os.path.exists(r'output_data'):
        os.mkdir(r'output_data')

    bonus_due_today.to_csv(
        'output_data/bonus_due_today.csv',
        index=False,
        header=False
    )

    bonus_due_today.loc[
        bonus_due_today['run_id'] <= 130,
        ['prolificID', 'bonus_GBP']] \
        .to_csv(
        'output_data/bonus_due_today_int.csv',
        index=False,
        header=False
    )

    bonus_due_today.loc[
        bonus_due_today['run_id'] > 130,
        ['prolificID', 'bonus_GBP']] \
        .to_csv(
        'output_data/bonus_due_today_us.csv',
        index=False,
        header=False
    )

    if len(bonus_due_today['due_on'].unique()) > 0:
        print(f'Some participants receive bonus today. '
              f'Check out the following: {bonus_due_today}')
    else:
        print('No subject awaits any bonus payment today')

    next_due_date = data.loc[
        (data['due_on'] > datetime.datetime.now().date()),
        'due_on'].min()
    print(f'Next due date: {next_due_date}')


save_data_bonus_due_today(data_pay)
