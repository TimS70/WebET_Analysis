import os

from data_prep.add_variables.choice.aoi import add_quadrant
from data_prep.clustering.create import add_clusters
from data_prep.clustering.select import find_aoi_clusters, filter_clusters
from utils.save_data import load_all_three_datasets, save_all_three_datasets
# agglomerative clustering
from numpy import unique
from numpy import where
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
import pandas as pd


def correct_clusters(data, clusters, aoi_width, aoi_height):

    corrected_data = []

    for quadrant in data['quadrant'].unique():

        x_center = clusters.loc[
            clusters['quadrant'] == quadrant,
            'x'].values[0]
        y_center = clusters.loc[
            clusters['quadrant'] == quadrant,
            'y'].values[0]

        data_this_aoi = data.loc[
            (data['x'] < x_center + aoi_width/2) &
            (data['x'] > x_center - aoi_width/2) &
            (data['y'] < y_center + aoi_height/2) &
            (data['y'] > y_center - aoi_height/2)] \
            .copy()

        x_deviation = clusters.loc[
            clusters['quadrant'] == quadrant,
            'x_deviation'].values[0]
        y_deviation = clusters.loc[
            clusters['quadrant'] == quadrant,
            'y_deviation'].values[0]

        data_this_aoi['x'] = data_this_aoi['x'] - x_deviation
        data_this_aoi['y'] = data_this_aoi['y'] - y_deviation
        data_this_aoi['aoi'] = quadrant

        corrected_data.append(data_this_aoi)

    return pd.concat(corrected_data)

