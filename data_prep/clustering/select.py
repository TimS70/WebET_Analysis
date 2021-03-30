import numpy as np
import pandas as pd

from data_prep.add_variables.choice.aoi import add_quadrant


def find_aoi_clusters(data, message, min_cluster_size, run):
    grouped_clusters = data \
        .groupby(['cluster'], as_index=False) \
        .agg(n_cluster=('x', 'count'),
             x=('x', 'mean'),
             y=('y', 'mean'))

    grouped_clusters = add_quadrant(grouped_clusters)

    data = add_quadrant(data)
    grouped_corners = data \
        .groupby(['quadrant'], as_index=False) \
        .agg(n_total=('x', 'count'))

    # Find largest clusters in each corner and compare
    # amount of gaze points within the cluster and the
    # total amount of gaze points
    aoi_clusters = grouped_clusters \
        .groupby(['quadrant'], as_index=False) \
        .agg(n_cluster=('n_cluster', 'max')) \
        .merge(grouped_clusters,
               on=['quadrant', 'n_cluster'],
               how='left') \
        .merge(grouped_corners,
               on='quadrant',
               how='left')

    aoi_clusters = aoi_clusters[
        aoi_clusters['n_cluster'] > min_cluster_size]

    if (len(aoi_clusters) < 4) & message:
        print(f'\n'
              f'Run {run} does not have large enough '
              f'clusters (n>{min_cluster_size}) in all 4 '
              f'corners and cannot be clustered')

    return aoi_clusters


def filter_clusters(aoi_clusters, min_ratio,
                    max_deviation, message, run=None):
    """
        min_ratio: Has to have more than x % of
            all dots in the corner within the cluster

        max_deviation: Should not deviate more than x %
            of the screen size from the respective AOI
    """

    aoi_clusters = aoi_clusters \
        .sort_values(by='quadrant') \
        .assign(n_ratio=aoi_clusters['n_cluster'] / \
                        aoi_clusters['n_total']) \
        .assign(x_deviation=aoi_clusters['x'] - \
                            pd.Series([0.25, 0.75, 0.25, 0.75])) \
        .assign(y_deviation=aoi_clusters['y'] - \
                            pd.Series([0.75, 0.75, 0.25, 0.25]))

    aoi_clusters['euclid_deviation'] = np.sqrt(
        aoi_clusters['x_deviation'] ** 2 +
        aoi_clusters['y_deviation'] ** 2)

    realistic_clusters = aoi_clusters[
        (aoi_clusters['n_ratio'] > min_ratio) &
        (aoi_clusters['euclid_deviation'] < max_deviation)]

    not_enough_gaze_points = len(aoi_clusters[
                                     (aoi_clusters['n_ratio'] > min_ratio)]) < 4

    too_far_away = len(aoi_clusters[
                           aoi_clusters[
                               'euclid_deviation'] < max_deviation]) < 4

    if message:
        if not_enough_gaze_points | too_far_away:
            print(f"""\nRun {run} could not be clustered: """)
            if not_enough_gaze_points:
                print(f"""   <{min_ratio * 100}% gaze point within """
                      f"""the AOIs for each corner""")
            if too_far_away:
                print(f"""   >{max_deviation * 100}% from where the AOI """
                      f"""is supposed to be \n""")

        else:
            print(f"""\nRun {run} can be clustered: """)

        print(f"""{aoi_clusters[[
            'quadrant', 'n_cluster', 'cluster', 'n_ratio',
            'x_deviation', 'y_deviation']]} \n"""
              f"""Notes: """)

    return realistic_clusters
