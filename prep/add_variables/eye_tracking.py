import numpy as np
import pandas as pd


def add_et_variables(data_et):
    data_et = invert_y_axis(data_et)
    data_et.to_csv(
        "data/added_var/data_et.csv",
        index=False, header=True)

    return data_et


def invert_y_axis(data_et):
    data_et['y'] = 1 - data_et['y']
    print('y_axis inverted')
    data_et['y'].describe()

    return data_et