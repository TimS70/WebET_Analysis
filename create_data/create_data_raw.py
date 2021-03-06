import datetime
import numpy as np
import math
import os
import pandas as pd
import re
import seaborn as sns
import json
import sys

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
from tqdm import tqdm


def create_data_raw():
    data_raw = compileData("data_prolific")
    survey_data = read_survey_data(data_raw)

    if 'prolificID' in data_raw.columns:
        data_raw = data_raw.drop(columns='prolificID')

    data_raw = data_raw \
        .merge(
        survey_data.loc[:, ['run_id', 'prolificID']],
        on='run_id',
        how='left'
    )

    data_raw['chinFirst'] = data_raw['chinFirst'].replace({'no': 0, 'yes': 1})

    return data_raw

def cleanhtml(raw_html):
    # https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
    cleanr = re.compile('<.*?>')
    cleanText = re.sub(cleanr, '', raw_html)

    return cleanText


def cleanETText(text):
    textWithinBrackets = re.findall(re.compile('\[.*?\]'), text)
    output = text
    for i in range(0, len(textWithinBrackets)):
        old = textWithinBrackets[i]
        new = re.sub(",", "$", old)
        output = output.replace(old, new)

    return output


def cleanSurveyText(text):
    output = text
    textWithinBrackets = re.findall(re.compile('\{.*?\}'), text)
    for i in range(0, len(textWithinBrackets)):
        old = textWithinBrackets[i]
        new = old.replace(',', '§')
        output = output.replace(old, new)

    return output


def compileData(path):
    subject_files = os.listdir(path)
    all_subjects = []
    for i in tqdm(range(0, len(subject_files))):
        csv_thisSubject = open(path + "/" + subject_files[i]).read()
        csv_thisSubject = cleanhtml(csv_thisSubject)
        csv_thisSubject = cleanETText(csv_thisSubject)
        csv_thisSubject = cleanSurveyText(csv_thisSubject)
        df_thisSubject = pd.read_csv(StringIO(csv_thisSubject))
        if len(df_thisSubject) > 0:
            all_subjects.append(df_thisSubject)
    output = pd.concat(all_subjects).reset_index(drop=True)

    return output


def find_prolific_ID_in_raw(this_ID):
    """
        Search for specific subjects
    :cvar
    """
    path = 'data_prolific'
    subject_files = os.listdir(path)
    for i in range(0, len(subject_files)):
        thisSubject_txt = open(path + "/" + subject_files[i]).read()
        if thisSubject_txt.find(this_ID) > (-1):
            print(f'ID {this_ID} is in {subject_files[i]}')
