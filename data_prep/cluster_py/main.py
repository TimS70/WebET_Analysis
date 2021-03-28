import os

from utils.save_data import load_all_three_datasets
# agglomerative clustering
from numpy import unique
from numpy import where
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
import pandas as pd

from visualize.eye_tracking import plot_et_scatter


def add_clusters(data):
    # define the model
    data = data \
        .loc[pd.notna(data['x']) & pd.notna(data['y']), :] \
        .reset_index(drop=True)

    model = AgglomerativeClustering(n_clusters=10)
    # fit model and predict clusters
    data['cluster'] = pd.Series(
        model.fit_predict(data[['x', 'y']]))

    run = round(data['run_id'].unique()[0])

    return data


def find_aoi_clusters(data):
    grouped_clusters = data \
        .groupby(['cluster'], as_index=False) \
        .agg(n=('x', 'count'),
             x_mean=('x', 'mean'),
             y_mean=('y', 'mean'))

    print(grouped_clusters)

    data_et = add_quadrant(data)



    grouped_corners = data

    exit()


def run_py_clustering():
    """
        Clustering: AOIs with certain gaze points and
        close to the actual position
    """

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'choice_task', 'added_var'))

    # First try 7, then 103
    for run in [7]: #data_et['run_id'].unique():

        data_et = add_clusters(
            data=data_et[data_et['run_id'] == run])

        plot_et_scatter(
            x=data_et['x'], y=data_et['y'], c=data_et['cluster'],
            title='Clusters for run ' +
                  str(run),
            file_name=str(run) + '.png',
            path=os.path.join('results', 'plots', 'clustering',
                              'py_clusters', 'all_clusters'))

        find_aoi_clusters(data_et)

        # print(clustered_this_run[['x', 'y']].describe())

        exit()
