import os

import scipy
import statsmodels.api as sm
from scipy import stats
from statsmodels.formula.api import ols

from utils.save_data import write_csv


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
    for var in outcomes:
        linear_model = ols((var + ' ~ ' + factor), data=data).fit()
        # Type 2 ANOVA DataFrame
        outcome_table = sm.stats.anova_lm(linear_model, typ=2)

        print(f"""{var} vs {factor} ANOVA: \n"""
              f"""{outcome_table} \n""")

        write_csv(data=outcome_table,
                  file_name='anova_' + var + '_vs_' + factor + '.csv',
                  path=os.path.join(path))
