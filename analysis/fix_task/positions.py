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


def compare_positions(data_trial_fix, outcome):
    outcome_by_position_long(data_trial_fix, outcome).head(5)

    outcome_by_position_wide(data_trial_fix, outcome)
    combinations = pos_combinations()
    position_tests = test_all_positions(outcome)

    example = position_tests.loc[position_tests['Sig'] != 'np'].head(5)

    print(
        f"""t-Tests for positions: \n"""
        f"""{example}""")


    test_top_vs_bottom_positions('offset')
    plot_top_vs_bottom_positions(data_trial_fix)

    test_left_vs_right_positions('offset')


def outcome_by_position_long(data_trial_fix, outcome_var):
    output_long = data_trial_fix.groupby(
        ['run_id', 'x_pos', 'y_pos'],
        as_index=False)[outcome_var].median()
    output_long['position'] = list(map(
        lambda x, y: str(x*100) + '%_' + str(y*100) + '%',
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
    output_long = data_trial_fix.groupby(
        ['run_id', 'x_pos', 'y_pos'],
        as_index=False)[outcome_var].median()
    output_long['position'] = list(map(
        lambda x, y: str(x * 100) + '%_' + str(y * 100) + '%',
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

    output_wide = pd.pivot_table(
        output_long,
        index='run_id',
        columns='position',
        values=outcome_var).reset_index()

    null_data = output_wide.loc[output_wide.isnull().any(axis=1), :]
    if len(null_data) > 0:
        print('! Attention ! Missing values')
        print(null_data)
    else:
        print('Success: No missing values found')

    return output_wide


def pos_combinations():
    cols = [
                '20.0%_20.0%', '20.0%_50.0%', '20.0%_80.0%',
                '50.0%_20.0%', '50.0%_50.0%', '50.0%_80.0%',
                '80.0%_20.0%', '80.0%_50.0%', '80.0%_80.0%'
            ]
    combinations = np.array(np.meshgrid(cols, cols)).T.reshape((-1, 2))

    for i in range(0, len(combinations)):
        combinations[i] = np.sort(combinations[i], axis=None)

    combinations = pd.DataFrame(combinations, columns=['col1', 'col2'])
    combinations = combinations \
        .loc[combinations['col1']!=combinations['col2'], :] \
        .drop_duplicates() \
        .reset_index(drop=True)
    print(f"""N combinations: {len(combinations)}""")
    return combinations


def test_all_positions(outcome_var):
    positions = outcome_by_position_wide(outcome_var)
    combinations = pos_combinations()

    all_results = []

    n = len(positions['run_id'].unique())

    for i in combinations.index:
        result = stats.ttest_rel(
            positions[combinations.loc[i, 'col1']],
            positions[combinations.loc[i, 'col2']])

        all_results.append([
            combinations.loc[i, 'col1'],
            combinations.loc[i, 'col2'],
            np.mean(positions[combinations.loc[i, 'col1']]),
            np.mean(positions[combinations.loc[i, 'col2']]),
            (result.statistic / np.sqrt(n)),
            result.statistic,
            result.pvalue])

    position_tests = pd.DataFrame(
        all_results,
        columns=[
            'position_1', 'position_2', 'position_1_mean', 'position_2_mean',
            'd', 't', 'p'])

    # Holm correction
    position_tests['p'] = smt.multipletests(position_tests['p'], method='holm')[1]

    position_tests['Sig'] = 'np'
    position_tests.loc[position_tests['p'] < 0.05, 'Sig'] = """*"""
    position_tests.loc[position_tests['p'] < 0.01, 'Sig'] = """**"""
    position_tests.loc[position_tests['p'] < 0.001, 'Sig'] = """***"""

    return position_tests


def test_top_vs_bottom_positions(outcome_var):
    offset_by_y_long = outcome_by_position_long(outcome_var) \
        .groupby(['run_id', 'y_pos'], as_index=False)[outcome_var].mean()
    offset_by_y_long = offset_by_y_long \
                           .loc[offset_by_y_long['y_pos'] != 0.5, :]

    offset_by_y_wide = pd.pivot_table(
        offset_by_y_long,
        index='run_id',
        columns='y_pos',
        values=outcome_var).reset_index()

    offset_by_y_wide.columns = ['run_id', '20%', '80%']
    result = stats.ttest_rel(
        offset_by_y_wide['20%'],
        offset_by_y_wide['80%']
    )

    n = len(offset_by_y_wide['run_id'].unique())
    print(f"""d: {(result.statistic / np.sqrt(n))}""")

    return result




# %% md

### Left vs. right

# %%

def test_left_vs_right_positions(outcome_var):
    offset_by_x_long = outcome_by_position_long(outcome_var) \
        .groupby(['run_id', 'x_pos'], as_index=False)[outcome_var].mean()
    offset_by_x_long = offset_by_x_long \
                           .loc[offset_by_x_long['x_pos'] != 0.5, :]

    offset_by_x_wide = pd.pivot_table(
        offset_by_x_long,
        index='run_id',
        columns='x_pos',
        values=outcome_var).reset_index()

    offset_by_x_wide.columns = ['run_id', '20%', '80%']
    result = stats.ttest_rel(
        offset_by_x_wide['20%'],
        offset_by_x_wide['80%']
    )

    n = len(offset_by_x_wide['run_id'].unique())
    print(f"""d: {(result.statistic / np.sqrt(n))}""")

    return result


def plot_top_vs_bottom_positions(data_trial_fix):
    offset_by_y_long = outcome_by_position_long(data_trial_fix, 'offset') \
        .groupby(['run_id', 'y_pos'], as_index=False)['offset'].mean()
    offset_by_y_long = offset_by_y_long.loc[
                       offset_by_y_long['y_pos'] != 0.5, :]

    fig, axes = plt.subplots(1, 1, sharey=True, figsize=(6, 6))
    fig.suptitle('Offset top vs. bottom ')

    sns.violinplot(ax=axes,
                   x='y_pos',
                   y='offset',
                   data=offset_by_y_long)
    makedir('results', 'plots', 'fix_task')
    plt.savefig(
        os.path.join('results', 'plots', 'fix_task', 'offset_top_vs_bottom.png'))
    plt.close()
