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


def init_cluster_correction(distance_threshold, min_cluster_size,
                            min_ratio, max_deviation,
                            aoi_width, aoi_height,
                            message):
    """
        Clustering: AOIs with certain gaze points and
        close to the actual position
    """

    data_et, data_trial, data_subject = load_all_three_datasets(
        path=os.path.join('data', 'choice_task', 'added_var'))

    print(f"""Run clustering for n="""
          f"""{len(data_et['run_id'].unique())} runs. \n""")

    data_et = data_et[data_et['t_task'] > 1000]

    data_et_corrected = []

    for run in tqdm(data_et['run_id'].unique(), desc='Run cluster correction: '):

        data_plot = data_et[
            pd.notna(data_et['aoi']) &
            ~data_et['aoi'].isin([0, '0'])]

        plot_et_scatter(
            x=data_plot['x'], y=data_plot['y'],
            title='Raw AOIs for run ' + str(run),
            file_name=str(round(run)) + '.png',
            path=os.path.join('results', 'plots', 'clustering',
                              'py_clusters', 'aoi_raw'))

        data_this = add_clusters(
            data=data_et.loc[data_et['run_id'] == run, :],
            distance_threshold=distance_threshold)

        plot_et_scatter(
            x=data_this['x'], y=data_this['y'], c=data_this['cluster'],
            title='Clusters for run #' + str(round(run)),
            label='distance=' + str(distance_threshold),
            file_name=str(round(run)) + '.png',
            path=os.path.join('results', 'plots', 'clustering',
                              'py_clusters', 'all_clusters'))

        aoi_clusters = find_aoi_clusters(
            data=data_this, message=message,
            min_cluster_size=min_cluster_size, run=run)

        data_plot = data_this[
            data_this['cluster'].isin(aoi_clusters['cluster'])]

        plot_et_scatter(
            x=data_plot['x'], y=data_plot['y'],
            c=data_plot['cluster'],
            title='Selected AOI clusters for run #' + str(round(run)),
            label='distance=' + str(distance_threshold),
            file_name=str(round(run)) + '.png',
            path=os.path.join('results', 'plots', 'clustering',
                              'py_clusters', 'aoi_clusters'))

        if len(aoi_clusters) < 4:
            continue

        aoi_clusters = filter_clusters(
            run=run,
            aoi_clusters=aoi_clusters,
            min_ratio=min_ratio,
            max_deviation=max_deviation,
            message=message)

        data_plot = data_this[
            data_this['cluster'].isin(aoi_clusters['cluster'])]

        plot_et_scatter(
            x=data_plot['x'], y=data_plot['y'],
            c=data_plot['cluster'],
            title='Filtered clusters for run #' + str(round(run)),
            label='distance=' + str(distance_threshold) + ' \n' +
                  'min_ratio=' + str(min_ratio) + ' \n' +
                  'max_deviation=' + str(max_deviation) + ' \n',
            file_name=str(round(run)) + '.png',
            path=os.path.join('results', 'plots', 'clustering',
                              'py_clusters', 'aoi_clusters_filtered'))

        # If clustering is not possible, skip this participant
        if len(aoi_clusters) < 4:
            continue

        corrected_data = correct_clusters(
            data=data_this, clusters=aoi_clusters,
            aoi_width=aoi_width, aoi_height=aoi_height)

        plot_et_scatter(
            x=corrected_data['x'], y=corrected_data['y'],
            title='AOI with corrected clusters for run #' + str(round(run)),
            file_name=str(round(run)) + '.png',
            path=os.path.join('results', 'plots', 'clustering',
                              'py_clusters', 'aoi_corrected'))

        data_et_corrected.append(corrected_data)

    data_et_corrected = pd.concat(data_et_corrected)

    print(f"""n={len(data_et_corrected['run_id'].unique())} """
          f"""runs of n={len(data_et['run_id'].unique())} """
          f"""runs could be clustered: \n"""
          f"""{data_et_corrected['run_id'].unique()}""")

    data_trial = data_trial[
        data_trial['run_id'].isin(data_et_corrected['run_id'].unique())]
    data_subject = data_subject[
        data_subject['run_id'].isin(data_et_corrected['run_id'].unique())]

    save_all_three_datasets(
        data_et_corrected, data_trial, data_subject,
        path=os.path.join('data', 'choice_task', 'added_var'))

    return data_et_corrected
