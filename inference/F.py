import scipy

from scipy import stats


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
