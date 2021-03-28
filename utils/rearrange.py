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
