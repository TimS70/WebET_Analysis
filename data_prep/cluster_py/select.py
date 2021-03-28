import os

from data_prep.add_variables.choice.aoi import add_quadrant
from utils.save_data import load_all_three_datasets, save_all_three_datasets
# agglomerative clustering
from numpy import unique
from numpy import where
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
import pandas as pd

from tqdm import tqdm

from visualize.eye_tracking import plot_et_scatter


def find_aoi_clusters(data, message, run):
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

    if (len(aoi_clusters) < 4) & message:
        print(f'Run {run} does not have clusters in all 4 '
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
        .assign(n_ratio=aoi_clusters['n_cluster'] / aoi_clusters['n_total']) \
        .assign(x_deviation=aoi_clusters['x'] - pd.Series([0.25, 0.75, 0.25, 0.75])) \
        .assign(y_deviation=aoi_clusters['y'] - pd.Series([0.75, 0.75, 0.25, 0.25]))

    realistic_clusters = aoi_clusters[
        (aoi_clusters['n_ratio'] > min_ratio) &
        (abs(aoi_clusters['x_deviation']) < max_deviation) &
        (abs(aoi_clusters['y_deviation']) < max_deviation)]

    not_enough_gaze_points = len(aoi_clusters[
        (aoi_clusters['n_ratio'] > min_ratio)]) < 4

    too_far_away = len(aoi_clusters[
       (abs(aoi_clusters['x_deviation']) < max_deviation) &
       (abs(aoi_clusters['y_deviation']) < max_deviation)]) < 4

    if message:
        if not_enough_gaze_points | too_far_away:
            print(f"""Run {run} could not be clustered: \n"""
                  f"""{aoi_clusters}""")
        if not_enough_gaze_points:
            print(f"""   <{min_ratio}% gaze point within """
                  f"""the AOIs for each corner""")
        if too_far_away:
            print(f"""   >{max_deviation}% from where the AOI """
                  f"""is supposed to be \n""")

    return realistic_clusters
