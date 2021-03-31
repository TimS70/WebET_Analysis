import numpy as np


def pivot_outcome_by_factor(data, factor, outcome):
    if len(data) > len(data['run_id'].unique()):
        outcomes_by_factor = data.groupby(
            ['run_id', factor],
            as_index=False)[outcome].mean()
    else:
        outcomes_by_factor = data[
            np.append(['run_id', factor], outcome)] \
            .drop_duplicates()

    outcomes_by_factor = outcomes_by_factor.pivot(index='run_id',
                                                  columns=factor,
                                                  values=outcome) \
        .reset_index(drop=True)

    return outcomes_by_factor
