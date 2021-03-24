import pandas as pd

from scipy import stats


# https://pythonfordatascienceorg.wordpress.com/welch-t-test-python-pandas/
def welch_ttest(x, y):
    ## Welch-Satterthwaite Degrees of Freedom ##
    dof = (x.var() / x.size + y.var() / y.size) ** 2 / (
                (x.var() / x.size) ** 2 / (x.size - 1) + (y.var() / y.size) ** 2 / (y.size - 1))

    t, p = stats.ttest_ind(x, y, equal_var=False)

    print("\n",
          f"""Descriptives: \n"""
          f"""{pd.DataFrame({'x': x, 'y': y}).describe()} \n\n"""
          f"""Welch's t-test= {t:.4f}; p = {p:.4f} \n""",
          f"""Welch-Satterthwaite Degrees of Freedom= {dof:.4f}""")


def welch_dof(x, y):
    dof = (x.var() / x.size + y.var() / y.size) ** 2 / (
            (x.var() / x.size) ** 2 / (x.size - 1) + (y.var() / y.size) ** 2 / (y.size - 1))
    # print(f"Welch-Satterthwaite Degrees of Freedom= {dof:.4f}")
