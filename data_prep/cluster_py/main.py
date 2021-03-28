import os

from data_prep.add_variables.choice.aoi import add_quadrant
from data_prep.cluster_py.correct import correct_clusters
from data_prep.cluster_py.create import add_clusters
from data_prep.cluster_py.select import find_aoi_clusters, filter_clusters
from utils.save_data import load_all_three_datasets, save_all_three_datasets, \
    write_csv
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

    data_et = pd.read_csv(os.path.join(
        'data', 'choice_task', 'added_var', 'data_et.csv'))

    data_et = data_et[data_et['t_task'] > 1000]

    all_corrected_data = []

    for run in tqdm(data_et['run_id'].unique(),
                    desc='Run cluster correction: '):

        data_this = add_clusters(
            data=data_et[data_et['run_id'] == run],
            distance_threshold=distance_threshold)

        data_plot = data_et[
            pd.notna(data_et['aoi']) &
            ~data_et['aoi'].isin([0, '0'])]

        plot_et_scatter(
            x=data_this['x'], y=data_this['y'], c=data_this['cluster'],
            title='Clusters for run ' + str(run),
            label='distance=' + str(distance_threshold),
            file_name=str(run) + '.png',
            path=os.path.join('results', 'plots', 'clustering',
                              'py_clusters', 'all_clusters'))

        aoi_clusters = find_aoi_clusters(data_this)

        data_plot = data_this[
            data_this['cluster'].isin(aoi_clusters['cluster'])]

        plot_et_scatter(
            x=data_plot['x'], y=data_plot['y'],
            c=data_plot['cluster'],
            title='Selected AOI clusters for run ' + str(run),
            label='distance=' + str(distance_threshold),
            file_name=str(run) + '.png',
            path=os.path.join('results', 'plots', 'clustering',
                              'py_clusters', 'aoi_clusters'))

        aoi_clusters = filter_clusters(
            aoi_clusters=aoi_clusters,
            min_ratio=min_ratio,
            max_deviation=max_deviation)

        data_plot = data_this[
            data_this['cluster'].isin(aoi_clusters['cluster'])]

        plot_et_scatter(
            x=data_plot['x'], y=data_plot['y'],
            c=data_plot['cluster'],
            title='Filtered clusters for run ' + str(run),
            label='distance=' + str(distance_threshold) + ' \n' +
                  'min_ratio=' + str(min_ratio) + ' \n' +
                  'max_deviation=' + str(max_deviation) + ' \n',
            file_name=str(run) + '.png',
            path=os.path.join('results', 'plots', 'clustering',
                              'py_clusters', 'aoi_clusters_filtered'))

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
            data=data_this, clusters=aoi_clusters,
            aoi_width=aoi_width, aoi_height=aoi_height)

        plot_et_scatter(
            x=corrected_data['x'], y=corrected_data['y'],
            title='AOI with corrected clusters for run ' + str(run),
            file_name=str(run) + '.png',
            path=os.path.join('results', 'plots', 'clustering',
                              'py_clusters', 'aoi_corrected'))

        all_corrected_data.append(corrected_data)

    all_corrected_data = pd.concat(all_corrected_data)

    write_csv(all_corrected_data, 'data_et.csv',
              os.path.join('data', 'choice_task',
                           'added_var'))
