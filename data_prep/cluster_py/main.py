import os

from data_prep.add_variables.choice.aoi import add_quadrant
from data_prep.cluster_py.create import add_clusters
from data_prep.cluster_py.select import find_aoi_clusters, filter_clusters
from utils.save_data import load_all_three_datasets, save_all_three_datasets
# agglomerative clustering
from numpy import unique
from numpy import where
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
import pandas as pd

from tqdm import tqdm

from visualize.eye_tracking import plot_et_scatter


def run_py_clustering(distance_threshold,
                      min_ratio, max_deviation):
    """
        Clustering: AOIs with certain gaze points and
        close to the actual position
    """

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'choice_task', 'added_var'))

    data_et = data_et[data_et['t_task'] > 1000]

    for run in [7]: # tqdm(data_et['run_id'].unique()[0], desc='Run cluster correction: '):

        this_data = data_et[data_et['run_id'] == run]

        this_data = add_clusters(
            data=this_data,
            distance_threshold=distance_threshold)

        # plot_et_scatter(
        #     x=this_data['x'], y=this_data['y'], c=this_data['cluster'],
        #     title='Clusters (distance=' + str(distance_threshold) +
        #           ') for run ' + str(run),
        #     file_name=str(run) + '.png',
        #     path=os.path.join('results', 'plots', 'clustering',
        #                       'py_clusters', 'all_clusters'))

        # save_all_three_datasets(
        #     data_et, data_trial, data_subject,
        #     'temp')

        largest_clusters = find_aoi_clusters(this_data)

        # data_et, data_trial, data_subject = load_all_three_datasets(
        #     'temp')

        largest_clusters = filter_clusters(
            largest_clusters=largest_clusters,
            min_ratio=min_ratio,
            max_deviation=max_deviation)


        # print(clustered_this_run[['x', 'y']].describe())

