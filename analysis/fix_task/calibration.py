import matplotlib.pyplot as plt

from utils.plots import spaghetti_plot, save_plot


# Median offset across calibration trials
# Does data quality improve during calibration?


def analyze_calibration(data_et, data_trial):
    data_et_calibration = data_et.loc[
                          data_et['trial_type'] == 'eyetracking-calibration', :]
    data_trial_calibration = data_trial.loc[
                             data_trial['trial_type'] == 'eyetracking-calibration', :]

    # Add median offset
    grouped = data_et_calibration \
        .groupby(['run_id', 'trial_index'])['offset'].median() \
        .reset_index() \
        .rename(columns={'offset': 'offset_median'})
    data_trial_calibration = data_trial_calibration.merge(
        grouped,
        on=['run_id', 'trial_index'],
        how='left'
    )

    plot_outcome_vs_trials(data_trial_calibration, 'offset_median', 103)
    plot_outcome_vs_trials(data_trial_calibration, 'precision', 103)


def plot_outcome_vs_trials(data_trial_calibration, outcome, run):
    spaghetti_plot(
        data_trial_calibration.loc[(
            (data_trial_calibration['chinFirst'] == 0) &
            (data_trial_calibration['chin'] == 0)
        ) | (
            (data_trial_calibration['chinFirst'] == 1) &
            (data_trial_calibration['chin'] == 1)
        ), :],
        'withinTaskIndex', outcome, run)

    plt.ylim(0, 1)
    plt.title((outcome + ' across calibration for chin==0'),
              loc='center', fontsize=12, fontweight=0, color='grey')
    plt.xlabel('withinTaskIndex')
    plt.ylabel(outcome)

    save_plot(
        ('calibration_' + outcome + '_vs_trials.png'),
        'results', 'plots', 'fix_task')