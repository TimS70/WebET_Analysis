import pandas as pd

from utils.save_data import write_csv


def filter_runs_not_us(data_subject):
    data_subject['residence'] = data_subject['Current Country of Residence']

    runs_not_us = data_subject.loc[
        data_subject['residence'] != 'United States', 'run_id']

    print(f"""{len(runs_not_us)} runs do not reside inside the us. """)

    return runs_not_us


def filter_runs_precision(data_subject, max_precision=0.15):
    runs_low_precision = data_subject.loc[
        data_subject['precision'] > max_precision, 'run_id']

    return runs_low_precision


def filter_runs_offset(data_subject, max_offset=0.5):
    runs_high_offset = data_subject.loc[
        data_subject['offset'] > max_offset, 'run_id']

    return runs_high_offset


def filter_hit_ratio(data_subject, min_hit_ratio=0.8):

    freq_table = pd.crosstab(
        index=data_subject['n_valid_dots'],
        columns="count")

    print(f"""How many dots are valid per subject. Dots during """
          f"""chin-rest validation: \n"""
          f"""{data_subject['n_valid_dots'].describe()} \n\n"""
          f"""{freq_table} \n\n"""
          f"""{data_subject[['run_id', 'fps', 'n_valid_dots']]}""")

    runs_low_hit_ratio = data_subject.loc[
        data_subject['hit_ratio'] < min_hit_ratio,
        'run_id']

    return runs_low_hit_ratio


def filter_bad_log_k(data_subject, max_noise=40):
    runs_missing_log_k = data_subject.loc[
        pd.isna(data_subject['logK']), 'run_id']

    runs_noisy_log_k = data_subject.loc[
        pd.notna(data_subject['logK']) &
        (data_subject['noise'] > max_noise), 'run_id']
    print(f"""Max allowed noise parameter (based on neg. log-likelihood): """
          f"""{max_noise}""")

    runs_pos_log_k = data_subject.loc[
        data_subject['logK'] > 0, 'run_id']

    return runs_missing_log_k, runs_noisy_log_k, runs_pos_log_k
