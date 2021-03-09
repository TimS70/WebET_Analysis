import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.stats.multitest as smt

from scipy import stats

from utils.path import makedir

# Correction
# Robert Rosenthal. The hand-book of research synthesis, chapter
# Parametric measures of effect size, pages 231–244.
# New York, NY: Russel Sage Foundation, 1994.
# t / sqrt n
from utils.tables import write_csv


def compare_positions(data_trial_fix, outcome):
    position_tests = test_all_positions(data_trial_fix, outcome)

    test_top_vs_bottom = test_top_vs_bottom_positions(
        data_trial_fix, outcome)

    test_left_vs_right = test_left_vs_right_positions(
        data_trial_fix, outcome)

    position_tests = pd.concat(
        [position_tests, test_top_vs_bottom, test_left_vs_right],
        ignore_index=True)

    # Holm correction
    position_tests['p'] = smt.multipletests(position_tests['p'],
                                            method='holm')[1]

    position_tests['Sig'] = 'np'
    position_tests.loc[position_tests['p'] < 0.05, 'Sig'] = """*"""
    position_tests.loc[position_tests['p'] < 0.01, 'Sig'] = """**"""
    position_tests.loc[position_tests['p'] < 0.001, 'Sig'] = """***"""

    significant_results = position_tests.loc[
        position_tests['Sig'] != 'np',
        ['position_1', 'position_2', 'd', 't', 'p']]

    if len(significant_results) > 0:
        print(
            f"""Significant results for {outcome}: \n"""
            f"""{significant_results}""")
    else:
        print(
            f"""No significant results for {outcome}. \n"""
        )

    write_csv(
        position_tests,
        (outcome + '_position_t_test.csv'),
        'results', 'tables', 'fix_task')

    plot_top_vs_bottom_positions(data_trial_fix, outcome)


def outcome_by_position_long(data_trial_fix, outcome_var):
    output_long = data_trial_fix.groupby(
        ['run_id', 'x_pos', 'y_pos'],
        as_index=False)[outcome_var].median()
    output_long['position'] = list(map(
        lambda x, y:
            str(round(x * 100, 0)) + '%_' +
            str(round(y * 100, 0)) + '%',
        output_long['x_pos'],
        output_long['y_pos']
    ))

    output_long['position_nr'] = output_long['position'] \
        .replace(
        [
            '20.0%_20.0%', '20.0%_50.0%', '20.0%_80.0%',
            '50.0%_20.0%', '50.0%_50.0%', '50.0%_80.0%',
            '80.0%_20.0%', '80.0%_50.0%', '80.0%_80.0%'
        ],
        np.arange(1, 10)
    )
    return output_long


def outcome_by_position_wide(data_trial_fix, outcome_var):
    output_long = outcome_by_position_long(
        data_trial_fix, outcome_var)

    output_wide = pd.pivot_table(
        output_long,
        index='run_id',
        columns='position',
        values=outcome_var).reset_index()

    # noinspection PyArgumentList
    null_data = output_wide.loc[output_wide.isnull().any(axis=1), :]
    if len(null_data) > 0:
        print(
            f"""! Attention: Missing values: \n"""
            f"""{null_data} \n""")
    else:
        print('Success: No missing values found. \n')

    return output_wide


def pos_combinations():
    cols = [
        '20.0%_20.0%', '20.0%_50.0%', '20.0%_80.0%',
        '50.0%_20.0%', '50.0%_50.0%', '50.0%_80.0%',
        '80.0%_20.0%', '80.0%_50.0%', '80.0%_80.0%'
    ]
    combinations = np.array(
        np.meshgrid(cols, cols)).T.reshape((-1, 2))

    for i in range(0, len(combinations)):
        combinations[i] = np.sort(combinations[i], axis=None)

    combinations = pd.DataFrame(
        combinations, columns=['col1', 'col2'])

    combinations = combinations.loc[
                   combinations['col1'] != combinations['col2'], :] \
        .drop_duplicates() \
        .reset_index(drop=True)
    print(
        f"""There are k ={len(combinations)} """
        f"""possible combinations of positions \n""")

    return combinations


def test_all_positions(data_trial_fix, outcome):
    positions_wide = outcome_by_position_wide(data_trial_fix, outcome)
    combinations = pos_combinations()

    all_results = []

    n = len(positions_wide['run_id'].unique())

    for i in combinations.index:
        result = stats.ttest_rel(
            positions_wide[combinations.loc[i, 'col1']],
            positions_wide[combinations.loc[i, 'col2']])

        all_results.append([
            combinations.loc[i, 'col1'],
            combinations.loc[i, 'col2'],
            np.mean(positions_wide[combinations.loc[i, 'col1']]),
            np.mean(positions_wide[combinations.loc[i, 'col2']]),
            (result.statistic / np.sqrt(n)),
            n,
            result.statistic,
            result.pvalue])

    position_tests = pd.DataFrame(
        all_results,
        columns=[
            'position_1', 'position_2', 'position_1_mean', 'position_2_mean',
            'd', 'n', 't', 'p'])

    return position_tests


def test_top_vs_bottom_positions(data_trial_fix, outcome):
    outcome_by_y_long = outcome_by_position_long(data_trial_fix, outcome) \
        .groupby(
        ['run_id', 'y_pos'],
        as_index=False)[outcome].mean()
    outcome_by_y_long = outcome_by_y_long.loc[
                        outcome_by_y_long['y_pos'] != 0.5, :]

    outcome_by_y_wide = pd.pivot_table(
        outcome_by_y_long,
        index='run_id',
        columns='y_pos',
        values=outcome).reset_index()

    outcome_by_y_wide.columns = ['run_id', '20%', '80%']
    t_test_result = stats.ttest_rel(
        outcome_by_y_wide['20%'],
        outcome_by_y_wide['80%']
    )

    n = len(outcome_by_y_wide['run_id'].unique())
    d = t_test_result.statistic / np.sqrt(n)

    output = pd.DataFrame({
        'position_1': ['bottom'],
        'position_2': ['top'],
        'position_1_mean': np.mean(outcome_by_y_wide['20%']),
        'position_2_mean': np.mean(outcome_by_y_wide['80%']),
        'd': [d],
        'n': [n],
        't': [t_test_result.statistic],
        'p': [t_test_result.pvalue]
    })

    return output


def test_left_vs_right_positions(data_trial_fix, outcome):
    outcome_by_x_long = outcome_by_position_long(data_trial_fix, outcome) \
        .groupby(
        ['run_id', 'x_pos'],
        as_index=False)[outcome].mean()
    outcome_by_x_long = outcome_by_x_long.loc[
                        outcome_by_x_long['x_pos'] != 0.5, :]

    outcome_by_x_wide = pd.pivot_table(
        outcome_by_x_long,
        index='run_id',
        columns='x_pos',
        values=outcome).reset_index()

    outcome_by_x_wide.columns = ['run_id', '20%', '80%']
    t_test_result = stats.ttest_rel(
        outcome_by_x_wide['20%'],
        outcome_by_x_wide['80%']
    )

    n = len(outcome_by_x_wide['run_id'].unique())
    d = t_test_result.statistic / np.sqrt(n)

    output = pd.DataFrame({
        'position_1': ['left'],
        'position_2': ['right'],
        'position_1_mean': np.mean(outcome_by_x_wide['20%']),
        'position_2_mean': np.mean(outcome_by_x_wide['80%']),
        'd': [d],
        'n': [n],
        't': [t_test_result.statistic],
        'p': [t_test_result.pvalue]
    })

    return output


def plot_top_vs_bottom_positions(data_trial_fix, outcome):
    outcome_by_y_pos = outcome_by_position_long(
        data_trial_fix, outcome) \
        .groupby(
        ['run_id', 'y_pos'],
        as_index=False)[outcome].mean()
    outcome_by_y_pos = outcome_by_y_pos.loc[
                       outcome_by_y_pos['y_pos'] != 0.5, :]

    fig, axes = plt.subplots(1, 1, sharey='none', figsize=(6, 6))
    fig.suptitle((outcome + ' top vs. bottom '))

    sns.violinplot(ax=axes,
                   x='y_pos',
                   y=outcome,
                   data=outcome_by_y_pos)

    makedir('results', 'plots', 'fix_task')
    plt.savefig(
        os.path.join('results', 'plots', 'fix_task',
                     (outcome + '_top_vs_bottom.png')))
    plt.close()
