import os

import numpy as np
import pandas as pd
from utils.save_data import write_csv
from visualize.all_tasks import save_plot
import seaborn as sns
import matplotlib.pyplot as plt


def combine_corr_matrix(data, variables):
    matrix_r = data[variables].rcorr(decimals=3, upper='n')
    matrix_r.index = matrix_r.index + '_r'

    matrix_p = data[variables].rcorr(decimals=3, upper='pval', stars=False)
    matrix_p.index = matrix_p.index + '_p'

    matrix_stars = data[variables].rcorr(decimals=3, upper='pval', stars=True)
    matrix_stars.index = matrix_stars.index + '_stars'

    matrix = pd.concat([matrix_r, matrix_p, matrix_stars]) \
        .sort_index(ascending=False)

    matrix_stars.index = matrix_r.index

    return matrix, matrix_stars


def clean_corr_data(data_plot):
    print('Cleaning data for correlation analysis...')
    null_data = data_plot[data_plot.isnull().any(axis=1)]

    if len(null_data) > 0:
        print('! Attention ! Missing values')
        print(f"""Length of data raw: {len(data_plot)} \n""")
    else:
        print('No missing data found')

    data_plot_clean = data_plot[~data_plot.isnull().any(axis=1)]
    print(f"""Length of data clean: {len(data_plot_clean)} \n""")

    return data_plot_clean


