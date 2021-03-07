import os
import re
import sys

import pandas as pd

from prep.load.survey_data import create_survey_data

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

from tqdm import tqdm


def combine_prolific_data(n_files='all'):
    data_raw = concat_csv_files(n_files)
    data_raw['chinFirst'] = data_raw['chinFirst'] \
        .replace({'no': 0, 'yes': 1})
    data_raw = add_survey_data(data_raw, 'prolificID')

    return data_raw


def concat_csv_files(n_files):
    path = 'data/cognition_run'
    subject_files = os.listdir(path)

    if n_files == 'all':
        n_files = len(subject_files)

    all_subjects = []

    for i in tqdm(range(0, n_files),
                  desc="Combining Prolific data"):
        this_csv = open(
            path + "/" + subject_files[i]).read()
        this_csv = clean_html(this_csv)
        this_csv = clean_et_text(this_csv)
        this_csv = clean_survey_text(this_csv)
        this_df = pd.read_csv(StringIO(this_csv))
        if len(this_df) > 0:
            all_subjects.append(this_df)

    data_raw = pd.concat(all_subjects).reset_index(drop=True)

    return data_raw


def clean_html(raw_html):
    # https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
    clean_r = re.compile('<.*?>')
    clean_text = re.sub(clean_r, '', raw_html)

    return clean_text


def clean_et_text(text):
    text_within_brackets = re.findall(re.compile('\[.*?\]'), text)
    output = text
    for i in range(0, len(text_within_brackets)):
        old = text_within_brackets[i]
        new = re.sub(",", "$", old)
        output = output.replace(old, new)

    return output


def clean_survey_text(text):
    output = text
    text_within_brackets = re.findall(re.compile('\{.*?\}'), text)
    for i in range(0, len(text_within_brackets)):
        old = text_within_brackets[i]
        new = old.replace(',', '§')
        output = output.replace(old, new)

    return output


def add_survey_data(data_raw, var_name):

    survey_data = create_survey_data(data_raw)

    if var_name in data_raw.columns:
        data_raw = data_raw.drop(columns=var_name)

    data_raw = data_raw \
        .merge(
            survey_data.loc[:, ['run_id', var_name]],
            on='run_id',
            how='left')

    return data_raw


def find_prolific_id_in_raw(this_id):
    """
        Search for specific subjects
    """
    path = 'data_prolific'
    subject_files = os.listdir(path)
    for i in range(0, len(subject_files)):
        this_subject_txt = open(path + "/" + subject_files[i]).read()
        if this_subject_txt.find(this_id) > (-1):
            print(f'ID {this_id} is in {subject_files[i]}')
