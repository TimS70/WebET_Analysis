import numpy as np
import pandas as pd


def invalid_choice_runs(data_trial, data_et, data_subject):
    runs_biasedChoices = data_subject.loc[
        (data_subject['choseLL'] > 0.99) |
        (data_subject['choseLL'] < 0.01),
        'run_id']

    grouped_trials_biased = data_trial.loc[
        data_trial['run_id'].isin(runs_biasedChoices), :] \
        .groupby(
            ['run_id', 'choseLL'],
            as_index=False).agg(
            n=('trial_index', 'count'))
    grouped_trials_biased = grouped_trials_biased \
        .loc[grouped_trials_biased['n'] > 1, :]

    print(
        f"""grouped_trials_biased \n"""
        f"""{grouped_trials_biased} \n"""
    )

    runs_missingLogK = data_subject.loc[
        pd.isna(data_subject['logK']), 'run_id']

    max_noise = 40
    runs_noisy_logK = data_subject.loc[
        pd.notna(data_subject['logK']) &
        (data_subject['noise'] > max_noise), 'run_id']
    print(
        f"""runs_noisy_logK means noise > {max_noise}. \n""")

    runs_pos_logK = data_subject.loc[
        data_subject['logK'] > 0, 'run_id']

    invalid_runs = list(
        set(runs_biasedChoices) |
        set(runs_missingLogK) |
        set(runs_noisy_logK) |
        set(runs_pos_logK))

    n_runs = len(data_trial['run_id'].unique())

    summary_output = pd.DataFrame(
        {
            'name': [
                'runs_biasedChoices',
                'runs_missingLogK',
                'runs_noisy_logK',
                'runs_pos_logK',
                'total',
            ],
            'length': [
                len(runs_biasedChoices),
                len(runs_missingLogK),
                len(runs_noisy_logK),
                len(runs_pos_logK),
                len(invalid_runs)
            ],
            'percent': [
                len(runs_biasedChoices) / n_runs,
                len(runs_missingLogK) / n_runs,
                len(runs_noisy_logK) / n_runs,
                len(runs_pos_logK) / n_runs,
                len(invalid_runs) / n_runs
            ]
        })

    print(
        f"""\n"""
        f"""n={n_runs} runs in total. Invalid runs for choice task: \n"""
        f"""{round(summary_output, 2)} \n""")

    return invalid_runs

