import pandas as pd
import scipy
import statsmodels.stats.multitest as smt
from scipy import stats

from analysis.fix_task.sight import plot_sight_vs_outcomes, anova_outcomes_sight
from visualize.all_tasks import split_violin_plot, violin_plot
from utils.tables import write_csv


def main_effect(data_trial_fix, data_subject):
    for outcome in ['offset', 'precision', 'fps']:
        violin_plot(data_trial_fix, outcome, 'chin')

    t_test_dep_outcomes_vs_factor(data_trial_fix, 'chin')

    for var in ['glasses', 'sight', 'glasses_binary']:
        freq_table = pd.crosstab(index=data_subject[var], columns="count")
        print(f"""{freq_table} \n""")
        write_csv(
            freq_table, ('glasses_freq_table_' + var),
            'results', 'tables', 'fix_task', 'main_effect')

    plot_sight_vs_outcomes(data_subject)
    anova_outcomes_sight(data_subject)

    t_test_ind_outcomes_vs_factor(data_subject, 'glasses_binary', '',
                                  'results', 'tables', 'fix_task',
                                  'main_effect')

    for outcome in ['offset', 'precision', 'fps']:
        split_violin_plot(data_trial_fix, outcome, 'chin', 'glasses_binary')

    # Check only those with high fps (Semmelmann & Weigelt, 2019)

    run_high_fps = data_subject.loc[
        data_subject['fps'] > data_subject['fps'].median(), 'run_id'].unique()

    data_subject_high_fps = data_subject.loc[
                            data_subject['run_id'].isin(run_high_fps), :]

    t_test_ind_outcomes_vs_factor(
        data_subject_high_fps, 'glasses_binary', 'high_fps',
        'results', 'tables', 'fix_task', 'main_effect')

    data_trial_fix_high_fps = data_trial_fix.loc[
                              data_trial_fix['run_id'].isin(run_high_fps), :]
    t_test_dep_outcomes_vs_factor(
        data_trial_fix_high_fps, 'chin', 'high_fps')


# noinspection DuplicatedCode,PyTypeChecker
def t_test_dep_outcomes_vs_factor(data_trial_fix, factor, note=''):
    outcomes_by_factor = pivot_outcomes_by_factor(data_trial_fix, factor)

    result_offset = t_test_rel('offset', outcomes_by_factor)
    result_precision = t_test_rel('precision', outcomes_by_factor)
    result_fps = t_test_rel('fps', outcomes_by_factor)

    summary = summarize_t_test_results(
        outcomes_by_factor,
        result_offset, result_precision, result_fps, True)

    if note != '':
        note = '_' + note

    write_csv(
        summary,
        ('t_test_' + factor + '_vs_outcomes' + str(note) + '.csv'),
        'results', 'tables', 'fix_task', 'main_effect')


def summarize_t_test_results(
        outcomes_by_factor,
        result_offset, result_precision, result_fps, dependent):

    summary = outcomes_by_factor.mean().reset_index() \
        .rename(columns={'level_0': 'measure', 0: 'mean'}) \
        .assign(SD=outcomes_by_factor.std().reset_index(drop=True)) \
        .assign(n=outcomes_by_factor.count().reset_index(drop=True))

    chin_test = pd.DataFrame({
        'measure': ['offset', 'precision', 'fps'],
        't': [
            result_offset.statistic,
            result_precision.statistic,
            result_fps.statistic
        ],
        'p': [
            result_offset.pvalue,
            result_precision.pvalue,
            result_fps.pvalue
        ]
    })

    chin_test['t'] = (chin_test['t']).astype(float)
    # Holm correction
    chin_test['p'] = smt.multipletests(
        chin_test['p'], method='holm')[1].astype(float)

    summary = summary.merge(
        chin_test,
        on='measure',
        how='left')

    if dependent:
        dependent_str = 'dependent'
    else:
        dependent_str = 'independent'

    print(
        f"""Summary from {dependent_str} t tests (holm-corrected): \n"""
        f"""{summary} \n""")

    return summary


def pivot_outcomes_by_factor(data, factor):
    if len(data) > len(data['run_id'].unique()):
        outcomes_by_factor = data.groupby(
            ['run_id', factor],
            as_index=False)[['offset', 'precision', 'fps']].mean()
    else:
        outcomes_by_factor = data.loc[:, [
            'run_id', factor, 'offset', 'precision', 'fps']] \
            .drop_duplicates()

    outcomes_by_factor = outcomes_by_factor.pivot(
        index='run_id',
        columns=factor,
        values=['offset', 'precision', 'fps'])

    return outcomes_by_factor


def t_test_rel(outcome, data_outcome_by_factor):
    return scipy.stats.ttest_rel(
        data_outcome_by_factor.loc[:, [(outcome, 0.0)]],
        data_outcome_by_factor.loc[:, [(outcome, 1.0)]]
    )


# noinspection PyTypeChecker
def t_test_ind_outcomes_vs_factor(data, factor, note='', *args):
    outcomes_by_factor = pivot_outcomes_by_factor(data, factor)

    result_offset = t_test_ind('offset', outcomes_by_factor)
    result_precision = t_test_ind('precision', outcomes_by_factor)
    result_fps = t_test_ind('fps', outcomes_by_factor)

    summary = summarize_t_test_results(
        outcomes_by_factor,
        result_offset, result_precision, result_fps, False)

    if note != '':
        note = '_' + note

    write_csv(
        summary,
        ('t_test_' + factor + '_vs_outcomes' + str(note) + '.csv'),
        *args)


def t_test_ind(outcome, data_outcome_by_factor):
    return scipy.stats.ttest_ind(
        data_outcome_by_factor.loc[:, [(outcome, 0.0)]].dropna(),
        data_outcome_by_factor.loc[:, [(outcome, 1.0)]].dropna()
    )
