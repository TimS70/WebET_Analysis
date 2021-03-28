import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils.add_next_trial import add_next_trial
from visualize.all_tasks import save_plot


def plot_incomplete_runs(data_trial):
    max_trial_by_run = data_trial \
        .groupby(['run_id'], as_index=False).agg(
            trial_index=('trial_index', 'max')) \
        .merge(
            data_trial[['run_id', 'trial_index',
                        'chinFirst', 'prolificID',
                        'trial_type_new', 'status']],
            on=['run_id', 'trial_index'],
            how='left')

    max_trial_by_run = add_next_trial(max_trial_by_run, data_trial)

    data_incomplete_runs = max_trial_by_run[
        max_trial_by_run['next_trial_type_new'] != 'end']

    data_plot = data_incomplete_runs \
        .groupby(['next_trial_type_new'],
                 as_index=False).agg(n=('run_id', 'count'))

    fig, ax = plt.subplots()
    ax.bar(data_plot['next_trial_type_new'], data_plot['n'])

    max_y = round(data_plot['n'].max() / 10) * 10
    ax.set_ylabel('Frequency')
    ax.yaxis.set_ticks(np.arange(0, max_y, 5))
    ax.set_title('Dropouts by trial type')

    fig.autofmt_xdate(rotation=45)

    plt.tight_layout()
    save_plot(file_name='dropouts.png',
              path=os.path.join('results', 'plots',
                                'dropouts'))
    plt.close()
