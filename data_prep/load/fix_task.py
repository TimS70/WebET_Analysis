from utils.combine import merge_by_index, merge_by_subject
from utils.save_data import load_all_three_datasets, save_all_three_datasets


def load_fix_data(path_origin, path_target):

    print('################################### \n'
          'Create fix task dataset \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(path_origin)

    data_et = merge_by_index(data_et, data_trial,
                             'task_nr', 'chin', 'chinFirst', 'trial_type',
                             'trial_duration', 'trial_duration_exact',
                             'x_pos', 'y_pos',
                             'window_width', 'window_height', 'x_count')

    data_trial = merge_by_subject(data_trial, data_subject, 'glasses_binary')

    print('for the fixation task, gaze points after 1000ms were selected. \n')
    data_et = data_et[
        (data_et['trial_type'] == 'eyetracking-fix-object') &
        (data_et['trial_duration'] == 5000) &
        (data_et['t_task'] > 1000)]

    data_trial = data_trial.loc[
        (data_trial['trial_type'] == 'eyetracking-fix-object') &
        (data_trial['trial_duration'] == 5000), [
            'run_id', 'prolificID', 'subject', 'chinFirst',
            'trial_index', 'task_nr', 'rt', 'stimulus', 'key_press',
            'time_elapsed', 'recorded_at', 'window_width', 'window_height',
            'success', 'chin', 'x_pos', 'y_pos', 'window_width_max',
            'window_height_max', 'window_diagonal_max', 'window_diagonal',
            't_startTrial', 'trial_duration', 'trial_duration_exact',
            'task_nr_new',
            'trial_type_new', 'trial_type_nr', 'fixTask', 'withinTaskIndex',
            'x_count', 'fps', 'glasses_binary'
        ]]

    save_all_three_datasets(data_et, data_trial, data_subject, path_target)
