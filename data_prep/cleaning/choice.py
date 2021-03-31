import numpy as np
import pandas as pd

from analysis.compare_datasets import check_unequal_trial_numbers
from data_prep.cleaning.drop_invalid_data.runs import clean_runs
from data_prep.cleaning.drop_invalid_data.trials import clean_trial_duration
from data_prep.cleaning.find_invalid_runs.both_tasks import filter_runs_low_fps
from data_prep.cleaning.find_invalid_runs.choice import filter_bad_log_k, \
    filter_runs_not_us, filter_runs_precision, filter_runs_offset, \
    filter_hit_ratio
from utils.combine import merge_by_index, combine_runs
from utils.save_data import save_all_three_datasets, \
    load_all_three_datasets


def clean_data_choice(
        path_origin, path_target,
        us_sample,
        min_hit_ratio, max_precision,
        max_offset, min_fps, min_rt, max_rt,
        min_choice_percentage, max_choice_percentage,
        exclude_runs=None, exclude_runs_reason=None,
        filter_log_k=True):
    print('################################### \n'
          'Clean choice data \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(path_origin)

    # Screening
    invalid_runs = []
    n_runs = len(data_trial['run_id'].unique())
    summary = []

    if us_sample:
        runs_not_us = filter_runs_not_us(data_subject)
        invalid_runs = combine_runs(invalid_runs, runs_not_us)
        summary.append(['runs_no_variance',
                        len(runs_not_us),
                        len(runs_not_us) / n_runs])

    if min_fps is not None:
        runs_low_fps = filter_runs_low_fps(
            data_trial, data_et, min_fps=min_fps)
        invalid_runs = combine_runs(invalid_runs, runs_low_fps)
        summary.append(['runs_low_fps',
                        len(runs_low_fps),
                        len(runs_low_fps) / n_runs])

    if max_precision is not None:
        runs_low_precision = filter_runs_precision(
            data_subject, max_precision=max_precision)
        invalid_runs = combine_runs(
            invalid_runs, runs_low_precision)
        summary.append(['runs_low_precision',
                        len(runs_low_precision),
                        len(runs_low_precision) / n_runs])

    if max_offset is not None:
        runs_high_offset = filter_runs_offset(
            data_subject, max_offset=max_offset)
        invalid_runs = combine_runs(invalid_runs, runs_high_offset)
        summary.append(['runs_high_offset',
                        len(runs_high_offset),
                        len(runs_high_offset) / n_runs])

    if min_hit_ratio is not None:
        runs_low_hit_ratio = filter_hit_ratio(
            data_subject, min_hit_ratio=min_hit_ratio)
        invalid_runs = combine_runs(invalid_runs, runs_low_hit_ratio)
        summary.append(['runs_low_hit_ratio',
                        len(runs_low_hit_ratio),
                        len(runs_low_hit_ratio) / n_runs])

    if exclude_runs is not None:
        runs_no_variance = np.intersect1d(
            data_subject['run_id'].unique(), exclude_runs)
        invalid_runs = combine_runs(invalid_runs, runs_no_variance)
        summary.append([exclude_runs_reason,
                        len(runs_no_variance),
                        len(runs_no_variance) / n_runs])

    if min_choice_percentage is not None:
        runs_biased_ss = data_subject.loc[
            data_subject['choseLL'] < min_choice_percentage, 'run_id']
        invalid_runs = combine_runs(invalid_runs, runs_biased_ss)
        summary.append(['runs_biased_SS',
                        len(runs_biased_ss),
                        len(runs_biased_ss) / n_runs])

    if max_choice_percentage is not None:
        runs_biased_ll = data_subject.loc[
            data_subject['choseLL'] > max_choice_percentage, 'run_id']
        invalid_runs = combine_runs(invalid_runs, runs_biased_ll)
        summary.append(['runs_biased_LL',
                        len(runs_biased_ll),
                        len(runs_biased_ll) / n_runs])

    if filter_log_k:
        runs_missing_log_k, runs_noisy_log_k, runs_pos_log_k = \
            filter_bad_log_k(data_subject, max_noise=40)
        invalid_runs = combine_runs(
            invalid_runs,
            runs_missing_log_k, runs_noisy_log_k,
            runs_pos_log_k)

        summary.append([
            'runs_missing_log_k',
            len(runs_missing_log_k),
            len(runs_missing_log_k) / n_runs])

        summary.append([
            'runs_noisy_log_k',
            len(runs_noisy_log_k),
            len(runs_noisy_log_k) / n_runs])

        summary.append([
            'runs_pos_log_k',
            len(runs_pos_log_k),
            len(runs_pos_log_k) / n_runs])

    summary.append(['total',
                    len(invalid_runs),
                    len(invalid_runs) / n_runs])

    summary = pd.DataFrame(summary, columns=['name', 'n', 'percent'])

    summary = summary.sort_values(by='n')

    print(f"""\nIn total, n={len(invalid_runs)} have to be """
          f"""removed from n={n_runs} runs: \n"""
          f"""{summary} \n""")

    # Remove invalid runs
    data_subject = clean_runs(data_subject, invalid_runs, 'data_subject')
    data_trial = clean_runs(data_trial, invalid_runs, 'data_trial')
    data_et = clean_runs(data_et, invalid_runs, 'data_et')

    if (min_rt is not None) & (max_rt is not None):
        # Remove Long trials
        data_trial = clean_trial_duration(
            data_trial, min_rt, max_rt, 'data_trial')

        data_et = merge_by_index(
            data_et, data_trial, 'trial_duration_exact')
        data_et = clean_trial_duration(
            data_et, min_rt, max_rt, 'data_et')
        data_et = data_et.drop(columns='trial_duration_exact')

    save_all_three_datasets(data_et, data_trial, data_subject, path_target)

    check_unequal_trial_numbers(data_et, data_trial)
