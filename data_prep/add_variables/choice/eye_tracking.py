import os
import subprocess

import numpy as np

from utils.combine_frames import merge_mean_by_subject


def add_et_indices_subject(data_subject, data_trial,
                           min_required_count):

    grouped = data_trial.groupby(
        ['run_id'],
        as_index=False).agg(
        attributeIndex=('attributeIndex', 'mean'),
        attributeIndex_n=('attributeIndex', 'count'),

        optionIndex=('optionIndex', 'mean'),
        optionIndex_n=('optionIndex', 'count'),

        payneIndex=('payneIndex', 'mean'),
        payneIndex_n=('payneIndex', 'count'),
    )

    print(
        f"""Aggregate ET indices on subject level. \n"""
        f"""Require >= {min_required_count} valid trials to aggregate """
        f"""on subject level. \n""")

    grouped.loc[
        grouped['attributeIndex_n'] < min_required_count,
        'attributeIndex'] = np.nan
    grouped.loc[
        grouped['optionIndex_n'] < min_required_count,
        'optionIndex'] = np.nan
    grouped.loc[
        grouped['payneIndex_n'] < min_required_count,
        'payneIndex'] = np.nan

    data_subject = merge_mean_by_subject(
        data_subject, grouped,
        'attributeIndex', 'optionIndex', 'payneIndex')

    print(
        f"""ET indices on subject level: \n"""
        f"""{data_subject[['attributeIndex', 'optionIndex', 
                           'payneIndex']].describe()} \n"""
    )

    return data_subject


def run_et_cluster_correction():
    print('Run cluster correction for eyetracking data. \n')
    os.chdir(os.path.join('data_prep', 'clustering'))

    # noinspection SpellCheckingInspection
    run_matlab = \
        'matlab -wait -nojvm -nosplash -nodesktop -r ' \
        '"init_clustering(14, 0.3, 0.3); exit"'

    subprocess.run(run_matlab, shell=True, check=True)

    os.chdir(os.path.join('../..', '..'))
