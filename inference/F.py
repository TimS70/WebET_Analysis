import os

import scipy
import statsmodels.api as sm
from scipy import stats
from statsmodels.formula.api import ols

from utils.save_data import write_csv
import pandas as pd


def compare_variances(data, factor, outcome):
    # Compare the variances
    summary = []
    for outcome in outcome:
        grouped = data \
            .groupby([factor], as_index=False) \
            .agg(n=('trial_index', 'count'),
                 mean=(outcome, 'mean'),
                 var=(outcome, 'var'))
        grouped['df'] = grouped['n'] - 1
        grouped['measure'] = outcome

        # Test that
        F, p_value = scipy.stats.levene(
            data.loc[data[factor] == 1, outcome],
            data.loc[data[factor] == 2, outcome])

        grouped[['F', 'p']] = [F, p_value]

        print(f"""{grouped} \n""")


def anova_outcomes_factor(data, outcomes, factor, path):
    summary = pd.DataFrame([],
                           columns=['sum_sq', 'df', 'F', 'PR(>F)', 'outcome'])

    for var in outcomes:
        linear_model = ols((var + ' ~ ' + factor), data=data).fit()
        # Type 2 ANOVA DataFrame
        outcome_table = sm.stats.anova_lm(linear_model, typ=2)

        outcome_table['outcome'] = var
        summary = summary.append(outcome_table)

    summary = summary[['outcome', 'sum_sq', 'df', 'F', 'PR(>F)']]

    summary['df'] = summary['df'].astype(int)
    summary[['sum_sq', 'F']] = round(summary[['sum_sq', 'F']], 2)
    summary[['PR(>F)']] = round(summary[['PR(>F)']], 3)

    print(f"""Outcomes vs {factor} ANOVA: \n"""
          f"""{summary} \n""")

    write_csv(data=summary,
              file_name='anova_outcomes_vs_' + factor + '.csv',
              path=os.path.join(path))
