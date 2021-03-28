import pandas as pd
import scipy
import statsmodels.stats.multitest as smt
from scipy import stats
# https://pythonfordatascienceorg.wordpress.com/welch-t-test-python-pandas/
from statsmodels.compat import scipy

from utils.rearrange import pivot_outcomes_by_factor
from utils.save_data import write_csv


def welch_ttest(x, y):
    ## Welch-Satterthwaite Degrees of Freedom ##
    dof = (x.var() / x.size + y.var() / y.size) ** 2 / (
            (x.var() / x.size) ** 2 / (x.size - 1) + (y.var() / y.size) ** 2 / (
                y.size - 1))

    t, p = stats.ttest_ind(x, y, equal_var=False)

    print("\n",
          f"""Descriptives: \n"""
          f"""{pd.DataFrame({'x': x, 'y': y}).describe()} \n\n"""
          f"""Welch's t-test= {t:.4f}; p = {p:.4f} \n""",
          f"""Welch-Satterthwaite Degrees of Freedom= {dof:.4f}""")


def welch_dof(x, y):
    dof = (x.var() / x.size + y.var() / y.size) ** 2 / (
            (x.var() / x.size) ** 2 / (x.size - 1) + (y.var() / y.size) ** 2 / (
                y.size - 1))
    # print(f"Welch-Satterthwaite Degrees of Freedom= {dof:.4f}")


# noinspection DuplicatedCode,PyTypeChecker
def t_test_dep_outcomes_vs_factor(data, factor, file_name):
    outcomes_by_factor = pivot_outcomes_by_factor(
        data, factor)

    result_offset = t_test_rel('offset', outcomes_by_factor)
    result_precision = t_test_rel('precision', outcomes_by_factor)
    result_fps = t_test_rel('fps', outcomes_by_factor)

    summary = summarize_t_test_results(
        outcomes_by_factor,
        result_offset, result_precision, result_fps, True)

    write_csv(
        summary,
        file_name,
        'results', 'tables', 'fix_task', 'main_effect')


def t_test_rel(outcome, data_outcome_by_factor):
    return stats.ttest_rel(
        data_outcome_by_factor.loc[:, [(outcome, 0.0)]],
        data_outcome_by_factor.loc[:, [(outcome, 1.0)]])


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

    print(f"""Summary from {dependent_str} t tests (holm-corrected): \n"""
          f"""{summary} \n""")

    return summary


# noinspection PyTypeChecker
def t_test_ind_outcomes_vs_factor(data, factor, file_name, path):
    outcomes_by_factor = pivot_outcomes_by_factor(data, factor)

    result_offset = t_test_ind('offset', outcomes_by_factor)
    result_precision = t_test_ind('precision', outcomes_by_factor)
    result_fps = t_test_ind('fps', outcomes_by_factor)

    summary = summarize_t_test_results(
        outcomes_by_factor,
        result_offset, result_precision, result_fps, False)

    write_csv(summary, file_name, path)


def t_test_ind(outcome, data_outcome_by_factor):
    return stats.ttest_ind(
        data_outcome_by_factor.loc[:, [(outcome, 0.0)]].dropna(),
        data_outcome_by_factor.loc[:, [(outcome, 1.0)]].dropna())
