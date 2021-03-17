import os

import pandas as pd

from IPython.display import HTML

from utils.path import makedir


def view(df):
    css = """<style>
    table { border-collapse: collapse; border: 3px solid #eee; }
    table tr th:first-child { background-color: #eeeeee; color: #333; font-weight: bold }
    table thead th { background-color: #eee; color: #000; }
    tr, th, td { border: 1px solid #ccc; border-width: 1px 0 0 1px; border-collapse: collapse;
    padding: 3px; font-family: monospace; font-size: 10px }</style>
    """
    s = '<script type="text/Javascript">'
    s += 'var win = window.open("", "Title", "toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=yes, resizable=yes, width=780, height=200, top="+(screen.height-400)+", left="+(screen.width-840));'
    s += 'win.document.body.innerHTML = \'' + (df.to_html() + css).replace("\n", '\\') + '\';'
    s += '</script>'
    return (HTML(s + css))


def load_all_three_datasets(path):
    data_et = pd.read_csv(
        os.path.join(path, 'data_et.csv'))
    data_trial = pd.read_csv(
        os.path.join(path, 'data_trial.csv'))
    data_subject = pd.read_csv(
        os.path.join(path, 'data_subject.csv'))

    print('Imported data from ' + path + ':')

    summarize_datasets(data_et, data_trial, data_subject)

    return data_et, data_trial, data_subject


def save_all_three_datasets_to(data_et, data_trial, data_subject, path):

    print('Data saved to ' + path + ':')

    makedir(path)

    data_et.to_csv(
        os.path.join(path, 'data_et.csv'),
        index=False, header=True)
    data_trial.to_csv(
        os.path.join(path, 'data_trial.csv'),
        index=False, header=True)
    data_subject.to_csv(
        os.path.join(path, 'data_subject.csv'),
        index=False, header=True)

    summarize_datasets(data_et, data_trial, data_subject)


def summarize_datasets(data_et, data_trial, data_subject):
    et_trial_count = data_et.groupby(
        ['run_id', 'trial_index'], as_index=False)['x'].count() \
        .loc[:, 'trial_index'].count()

    summary = pd.DataFrame(
        {'dataset':
            [
                'data_et',
                'data_trial',
                'data_subject'
            ],
            'prolific_ids':
                [
                    '-',
                    len(data_trial['prolificID'].unique()),
                    len(data_subject['prolificID'].unique()),
                ],
            'runs':
                [
                    len(data_et['run_id'].unique()),
                    len(data_trial['run_id'].unique()),
                    len(data_subject['run_id'].unique()),
                ],
            'n_trials':
                [
                    et_trial_count,
                    len(data_trial),
                    '-'
                ]
        }
    )
    print(f"""{summary} \n""")


def write_csv(data_frame, file_name, *args):
    makedir(*args)
    path = os.path.join(*args)
    data_frame.to_csv(os.path.join(path, file_name))
    print(
        f"""Results '{file_name}' written to {path} \n""")
