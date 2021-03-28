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


def add_clusters(data, distance_threshold):

    # define the model
    data = data[pd.notna(data['x']) & pd.notna(data['y'])]

    model = AgglomerativeClustering(
        n_clusters=None,
        linkage='average',
        distance_threshold=distance_threshold)
    # fit model and predict clusters
    data['cluster'] = pd.Series(
        model.fit_predict(data[['x', 'y']]))

    run = round(data['run_id'].unique()[0])

    return data