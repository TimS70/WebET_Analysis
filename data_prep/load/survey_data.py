import re
import sys

import pandas as pd

if sys.version_info[0] < 3:
    # noinspection PyUnresolvedReferences
    from StringIO import StringIO
else:
    from io import StringIO

from tqdm import tqdm


def create_survey_data(data, show_notes=False):
    """
        survey data (to merge with data_subject)
    """
    survey_data = pd.DataFrame(columns=[
        'prolificID', 'age', 'gender', 'ethnic', 'sight',
        'glasses', 'degree', 'eyeshadow', 'masquara', 'eyeliner',
        'browliner', 'vertPosition', 'triedChin', 'keptHead',
        'optionalNote', 'run_id'])

    for subject in tqdm(
            data['run_id'].unique(),
            desc='Read survey data'):

        df_this_subject = data.loc[
            (data['run_id'] == subject) &
            (pd.notna(data["responses"])) &
            (data["responses"] != '"'),
            ['run_id', 'responses']
        ] \
            .reset_index()

        if len(df_this_subject) > 0:
            survey_data = \
                survey_data.append(
                    survey_data_this_run(
                        df_this_subject
                    )
                )

    survey_data = survey_data.rename(columns={'age': 'birthyear'})
    survey_data = clean_binary_survey_data(survey_data)

    if show_notes:
        show_optional_notes(survey_data)

    return survey_data


def clean_optional_note(text):
    optional_note_text = re.findall(re.compile('optionalNote":.*?}'), text)
    if len(optional_note_text) < 1:
        output = text
    else:
        old = optional_note_text[0]
        new = old.replace('§', ' ') \
            .replace(':', ' ') \
            .replace('(', ' ') \
            .replace(')', ' ') \
            .replace('optionalNote" ', 'optionalNote":')

        output = text.replace(old, new)
    return output


def survey_string_to_frame(string):
    string = clean_optional_note(string)
    string = re.sub("""{""", '', string)
    string = re.sub("""}""", '', string)
    string = re.sub('"', '', string)
    string = re.sub('§', '$', string)
    output = pd.read_csv(StringIO(string),
                         sep=":",
                         lineterminator="$",
                         header=None,
                         index_col=0
                         ).transpose()
    return output


def survey_data_this_run(data):
    subject = data['run_id'].unique()[0]
    output = []
    for i in range(0, len(data)):
        output.append(
            survey_string_to_frame(
                data.loc[i, 'responses']))

    output = pd.concat(output, axis=1)
    output['run_id'] = subject

    return output


def show_optional_notes(survey_data):
    data_optional_notes = survey_data.loc[
        pd.notna(survey_data['optionalNote']),
        ['run_id', 'optionalNote']
    ]

    for subject in data_optional_notes['run_id'].unique():
        print(f'run_id: {subject}')
        print(data_optional_notes.loc[
                  data_optional_notes['run_id'] == subject,
                  'optionalNote'].values[0])
        print('\n')


def clean_binary_survey_data(data):
    columns = [
        'eyeshadow',
        'masquara',
        'eyeliner',
        'browliner',
        'triedChin',
        'keptHead'
    ]

    for col in columns:
        data[col] = data[col].replace({'no': 0, 'yes': 1})

    return data