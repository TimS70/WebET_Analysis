import pandas as pd

from utils.save_data import write_csv


def filter_runs_not_us(data_subject):
    data_subject['residence'] = data_subject['Current Country of Residence']

    runs_not_us = data_subject.loc[
        data_subject['residence'] != 'United States', 'run_id']

    data_subject['residence'] = 'us'
    data_subject.loc[
        data_subject['run_id'].isin(runs_not_us),
        'residence'] = 'international'

    grouped_us = data_subject.groupby(
        ['residence'],
        as_index=False).agg(
        n=('run_id', 'count'),
        attributeIndex=('attributeIndex', 'mean'),
        attributeIndex_std=('attributeIndex', 'std'),
        optionIndex=('optionIndex', 'mean'),
        optionIndex_std=('optionIndex', 'std'),
        payneIndex=('payneIndex', 'mean'),
        payneIndex_std=('payneIndex', 'std'),
        choseLL=('choseLL', 'mean'),
        choseLL_std=('choseLL', 'std'),
        choseTop=('choseTop', 'mean'),
        choseTop_std=('choseTop', 'std'),
        logK=('logK', 'mean'),
        logK_std=('logK', 'std'),
        choice_rt=('choice_rt', 'mean'),
        choice_rt_std=('choice_rt', 'std'),
        offset=('offset', 'mean'),
        offset_std=('offset', 'std'),
        precision=('precision', 'mean'),
        precision_std=('precision', 'std'),
        fps=('fps', 'mean'),
        fps_std=('fps', 'std')).T

    write_csv(grouped_us, 'us_vs_international_sample.csv',
              'results', 'tables', 'demographics')

    print(
        f"""{len(runs_not_us)} runs do not reside inside the us. """
        f"""However, since their behavior does not differ much, """
        f"""we will keep them for now. \n \n"""
        f"""grouped_us.transpose: \n"""
        f"""{grouped_us} \n""")

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
