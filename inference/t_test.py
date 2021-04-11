import pandas as pd
import scipy
import statsmodels.stats.multitest as smt
from scipy import stats
# https://pythonfordatascienceorg.wordpress.com/welch-t-test-python-pandas/
from statsmodels.compat import scipy

from utils.rearrange import pivot_outcome_by_factor
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
def t_test_outcomes_vs_factor(data, dependent, factor,
                              file_name, outcomes, path):

    print(f"""t-test for {factor}: """)
    result_summary = []
    describe_outcomes = pd.DataFrame(
        columns=['outcome', factor, 'n', 'mean', 'SD'])

    for var in outcomes:
        # t-test
        outcome_by_factor = pivot_outcome_by_factor(
            data, factor, var)

        print(outcome_by_factor)
        exit()
        if dependent:
            t_test_result = t_test_rel(outcome_by_factor)
        else:
            t_test_result = t_test_ind(outcome_by_factor)

        result_summary.append(
            [var,
             t_test_result.statistic.astype(float),
             t_test_result.pvalue.astype(float)])

        # Descriptives
        summary_this_outcome = data \
            .groupby([factor], as_index=False) \
            .agg(n=('run_id', 'nunique'),
                 mean=(var, 'mean'),
                 SD=(var, 'std')) \
            .assign(outcome=var)

        describe_outcomes = describe_outcomes.append(
            summary_this_outcome)

    result_summary = pd.DataFrame(result_summary,
                                  columns=['outcome', 't', 'p'])

    # Holm correction
    result_summary['p'] = smt.multipletests(
        result_summary['p'], method='holm')[1].astype(float)

    summary = describe_outcomes.merge(
        result_summary, on='outcome', how='left')

    note = 'dependent' if dependent else 'independent'

    print(f"""Summary from {note} t tests """
          f"""(holm-corrected): \n"""
          f"""{summary} \n""")

    write_csv(data=summary, file_name=file_name, path=path)


def t_test_rel(data_outcome_by_factor):
    return stats.ttest_rel(
        data_outcome_by_factor.iloc[:, 0],
        data_outcome_by_factor.iloc[:, 1])


def t_test_ind(data_outcome_by_factor):
    return stats.ttest_ind(
        data_outcome_by_factor.iloc[:, 0].dropna(),
        data_outcome_by_factor.iloc[:, 1].dropna())
