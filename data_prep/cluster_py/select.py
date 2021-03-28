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


def find_aoi_clusters(data):
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
    largest_clusters = grouped_clusters \
        .groupby(['quadrant'], as_index=False) \
        .agg(n_cluster=('n_cluster', 'max')) \
        .merge(grouped_clusters,
               on=['quadrant', 'n_cluster'],
               how='left') \
        .merge(grouped_corners,
               on='quadrant',
               how='left')

    return largest_clusters


def filter_clusters(largest_clusters, min_ratio,
                    max_deviation):
    """
        min_ratio: Has to have more than x % of
            all dots in the corner within the cluster

        max_deviation: Should not deviate more than x %
            of the screen size from the respective AOI
    """

    largest_clusters = largest_clusters.sort_values(
        by='quadrant')

    largest_clusters['n_ratio'] = \
        largest_clusters['n_cluster'] / \
        largest_clusters['n_total']

    largest_clusters['x_deviation'] = abs(largest_clusters['x'] - \
        pd.Series([0.25, 0.75, 0.25, 0.75]))

    largest_clusters['y_deviation'] = abs(largest_clusters['y'] - \
        pd.Series([0.75, 0.75, 0.25, 0.25]))

    largest_clusters = largest_clusters[
        (largest_clusters['x_deviation'] < max_deviation) &
        (largest_clusters['y_deviation'] < max_deviation)]

    largest_clusters = largest_clusters[
        largest_clusters['n_ratio'] > min_ratio]

    print(round(largest_clusters, 2))

    return largest_clusters
