import os

from data_prep.add_variables.choice.aoi import add_quadrant
from data_prep.cluster_py.correct import correct_clusters
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
                      min_ratio, max_deviation,
                      aoi_width, aoi_height):
    """
        Clustering: AOIs with certain gaze points and
        close to the actual position
    """

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'choice_task', 'added_var'))

    data_et = data_et[data_et['t_task'] > 1000]

    for run in [7]: # tqdm(data_et['run_id'].unique()[0], desc='Run cluster correction: '):

        this_data = add_clusters(
            data=data_et[data_et['run_id'] == run],
            distance_threshold=distance_threshold)

        print(f"""Before clustering: \n"""
              f"""{data_et[['x', 'y']].describe()} \n""")

        plot_et_scatter(
            x=this_data['x'], y=this_data['y'], c=this_data['cluster'],
            title='Clusters (distance=' + str(distance_threshold) +
                  ') for run ' + str(run),
            file_name=str(run) + '.png',
            path=os.path.join('results', 'plots', 'clustering',
                              'py_clusters', 'all_clusters'))

        aoi_clusters = find_aoi_clusters(this_data)
        aoi_clusters = filter_clusters(
            aoi_clusters=aoi_clusters,
            min_ratio=min_ratio,
            max_deviation=max_deviation)

        # If clustering is not possible, skip this participant
        if len(aoi_clusters) < 4:
            print(f"""Run {run} does not have clear AOIs """
                  f"""and cannot be clustered: \n"""
                  f""" - <{min_ratio}% gaze point within """
                  f"""the AOIs for each corner \n"""
                  f"""> {max_deviation}% from where the AOI """
                  f"""is supposed to be \n""")

            continue

        corrected_data = correct_clusters(
            data=this_data, clusters=aoi_clusters,
            aoi_width=aoi_width, aoi_height=aoi_height)

        print(f"""Before clustering: \n"""
              f"""{corrected_data[['x', 'y']].describe()} \n""")

        # print(clustered_this_run[['x', 'y']].describe())

