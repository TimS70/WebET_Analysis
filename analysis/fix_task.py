import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import os
import pandas as pd
import pingouin as pg
import seaborn as sns
import scipy
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import silhouette_score
import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels.graphics.api as smg
import statsmodels.stats.multitest as smt
from statsmodels.formula.api import ols
import sys

from data_prep.add_variables.data_quality import euclideanDistance
from utils.path import makedir


def plot_gaze_shift(data_et, data_trial):
    data_et_fix_task_fixCross = reformatTTask(select_fixTask_and_fixCross(data_et))
    data_trial_fix_task_fixCross = add_next_xy_pos(select_fixTask_and_fixCross(data_trial))

    data_et_fix_task_fixCross = data_et_fix_task_fixCross.merge(
        data_trial_fix_task_fixCross.loc[:, ['run_id', 'trial_index', 'next_x_pos', 'next_y_pos']],
        on=['run_id', 'trial_index'],
        how='left'
    )
    data_et_fix_task_fixCross = new_distance_for_fixCross(data_et_fix_task_fixCross)
    average_line_noChin = createAVGLine(data_et_fix_task_fixCross.loc[data_et_fix_task_fixCross['chin'] == 0, :])
    average_line_chin = createAVGLine(data_et_fix_task_fixCross.loc[data_et_fix_task_fixCross['chin'] == 1, :])

    # %%

    fig, axes = plt.subplots(nrows=1, ncols=2, sharey=True, figsize=(18, 12))
    fig.suptitle('Median local offset for all subjects across a fixation task trial', fontsize=20)

    axes[0].set_title("Chin==0")
    axes[1].set_title("Chin==1")

    sns.scatterplot(ax=axes[0],
                    data=data_et_fix_task_fixCross.loc[
                         (data_et_fix_task_fixCross['run_id'] == 103) &
                         (data_et_fix_task_fixCross['chin'] == 0),
                         :],
                    x="t_task", y="offset")
    sns.lineplot(ax=axes[0], x=average_line_noChin['t_task'], y=average_line_noChin['offset'], color='r')

    sns.scatterplot(ax=axes[1],
                    data=data_et_fix_task_fixCross.loc[
                         (data_et_fix_task_fixCross['run_id'] == 103) &
                         (data_et_fix_task_fixCross['chin'] == 1),
                         :],
                    x="t_task", y="offset")
    sns.lineplot(ax=axes[1], x=average_line_chin['t_task'], y=average_line_chin['offset'], color='r')

    plt.setp(axes, xlim=(-1500, 5000))
    plt.xlabel("t_task")

    makedir('results', 'plots', 'fix_task')
    plt.savefig(
        os.path.join('results', 'plots', 'fix_task', 'offset_gaze_shift.png'))
    plt.close()


def select_fixTask_and_fixCross(data):
    return data.loc[
           (data['trial_type'] == 'eyetracking-fix-object') &
           ((data['task_nr'] == 1) |
            ((data['chinFirst'] == 0) & (data['task_nr'] == 2)) |
            ((data['chinFirst'] == 1) & (data['task_nr'] == 3))
            ), :].reset_index(drop=True)


def reformatTTask(data):
    data.loc[
        (data['trial_type'] == 'eyetracking-fix-object') &
        (data['trial_duration'] == 1500),
        't_task'
    ] = data.loc[
            (data['trial_type'] == 'eyetracking-fix-object') &
            (data['trial_duration'] == 1500),
            't_task'
        ] - 1500
    return data


def add_next_xy_pos(data):
    data['next_x_pos'] = 0
    data['next_y_pos'] = 0
    for i in data.index:
        if data.loc[i, 'trial_duration'] == 1500:
            data.loc[i, 'next_x_pos'] = data.loc[i + 1, 'x_pos']
            data.loc[i, 'next_y_pos'] = data.loc[i + 1, 'y_pos']
    return (data)


def new_distance_for_fixCross(data):
    data.loc[data['trial_duration'] == 1500, 'offset'] = euclideanDistance(
        data.loc[data['trial_duration'] == 1500, 'x'],
        data.loc[data['trial_duration'] == 1500, 'next_x_pos'],
        data.loc[data['trial_duration'] == 1500, 'y'],
        data.loc[data['trial_duration'] == 1500, 'next_y_pos']
    )
    return data


def createAVGLine(data):
    binArray = np.arange(-1500, 5000, 50)
    bins = pd.cut(data['t_task'], binArray)
    output = data.groupby(bins).agg({"offset": "median"}).reset_index()
    output['t_task'] = binArray[0:len(output)]
    return output
