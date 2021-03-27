import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols

from visualize.all_tasks import save_plot
from utils.save_data import write_csv


def plot_sight_vs_outcomes(data_subject):
    for outcome in ['offset', 'precision', 'fps']:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 8))
        fig.suptitle((outcome + 'vs sight'), fontsize=20)

        sns.boxplot(ax=ax, x='sight', y=outcome, data=data_subject)

        ax.tick_params(labelrotation=45, labelsize=13)
        ax.tick_params(axis='y', labelrotation=None)

        nobs = data_subject['sight'].value_counts().values
        nobs = [str(x) for x in nobs.tolist()]
        nobs = ["n: " + i for i in nobs]
        # Add it to the plot
        pos = range(len(nobs))

        max_value = data_subject[outcome].max()
        y_pos = max_value + max_value * 0.1

        for tick, label in zip(pos, ax.get_xticklabels()):
            ax.text(
                pos[tick], y_pos, nobs[tick],
                verticalalignment='top',
                horizontalalignment='center', size=13, weight='normal')

        save_plot((outcome + '_vs_sight'),
                  'results', 'plots', 'fix_task', 'main_effect', 'sight')


def anova_outcomes_sight(data_subject):
    for var in ['offset', 'precision', 'fps']:
        sight_lm = ols((var + ' ~ sight'), data=data_subject).fit()
        outcome_table = sm.stats.anova_lm(sight_lm, typ=2)  # Type 2 ANOVA DataFrame

        print(
            f"""{var} vs sight ANOVA: \n"""
            f"""{outcome_table} \n"""
        )

        write_csv(outcome_table, ('anova_' + var + '_vs_sight'),
                  'results', 'tables', 'fix_task', 'sight')
