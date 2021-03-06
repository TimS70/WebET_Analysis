def cleanOptionalNote(text):
    optionalNoteText = re.findall(re.compile('optionalNote":.*?\}'), text)
    if len(optionalNoteText) < 1:
        output = text
    else:
        old = optionalNoteText[0]
        new = old.replace('§', ' ') \
            .replace(':', ' ') \
            .replace('(', ' ') \
            .replace(')', ' ') \
            .replace('optionalNote" ', 'optionalNote":')

        output = text.replace(old, new)
    return output


def surveyStringToFrame(subject, string):
    string = cleanOptionalNote(string)
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

def surveyData_thisSubject(data):
    subject = data['run_id'].unique()[0]
    output = []
    for i in range(0, len(data)):
        output.append(
            surveyStringToFrame(subject,
                                data.loc[i, 'responses'])
        )

    output = pd.concat(output, axis=1)
    output['run_id'] = subject

    return output


def read_survey_data(data, show_notes=False):
    """:cvar
        survey data (to merge with data_subject)
    """
    surveyData = pd.DataFrame(columns=[
        'prolificID', 'age', 'gender', 'ethnic', 'sight',
        'glasses', 'degree', 'eyeshadow', 'masquara', 'eyeliner',
        'browliner', 'vertPosition', 'triedChin', 'keptHead',
        'optionalNote', 'run_id'])

    for subject in tqdm(data['run_id'].unique()):

        df_thisSubject = data.loc[
            (data['run_id'] == subject) &
            (pd.notna(data["responses"])) &
            (data["responses"] != '"'),
            ['run_id', 'responses']
        ] \
            .reset_index()

        if len(df_thisSubject) > 0:
            surveyData = \
                surveyData.append(
                    surveyData_thisSubject(
                        df_thisSubject
                    )
                )

    surveyData = surveyData.rename(columns={'age': 'birthyear'})
    surveyData = clean_binary_survey_data(surveyData)

    if show_notes:
        show_optional_notes(surveyData)

    return (surveyData)


def show_optional_notes(survey_data):
    data_optionalNotes = survey_data.loc[
        pd.notna(survey_data['optionalNote']),
        ['run_id', 'optionalNote']
    ]

    for subject in data_optionalNotes['run_id'].unique():
        print(f'run_id: {subject}')
        print(data_optionalNotes.loc[
                  data_optionalNotes['run_id'] == subject,
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