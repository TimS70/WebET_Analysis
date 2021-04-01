import os

from inference.t_test import t_test_outcomes_vs_factor
from visualize.all_tasks import violin_plot


def test_chin_rest(data_trial, data_subject, path_plots, path_tables):

    # Chin-rest vs. hit-ratio, etc.
    for outcome in ['offset', 'precision', 'fps', 'hit_mean']:
        violin_plot(data=data_trial,
                    outcome=outcome, factor='chin',
                    path=os.path.join(path_plots))

    t_test_outcomes_vs_factor(data=data_trial,
                              dependent=True,
                              factor='chin',
                              outcomes=['offset', 'precision', 'fps',
                                        'hit_mean'],
                              file_name='t_test_chin_vs_outcomes.csv',
                              path=os.path.join(path_tables))

    # Check only those with high fps (Semmelmann & Weigelt, 2019)
    run_high_fps = data_subject.loc[
        data_subject['fps'] > data_subject['fps'].median(),
        'run_id'].unique()

    data_subject_high_fps = data_subject[
        data_subject['run_id'].isin(run_high_fps)]

    t_test_outcomes_vs_factor(
        data=data_trial,
        dependent=True,
        factor='chin',
        outcomes=['offset', 'precision', 'fps', 'hit_mean'],
        file_name='t_test_chin_vs_outcomes_high_fps.csv',
        path=os.path.join(path_tables))
