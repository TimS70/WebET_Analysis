from utils.combine import merge_by_index, merge_by_subject
from utils.save_data import load_all_three_datasets, save_all_three_datasets
import numpy as np


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
            'success', 'chin', 'x_pos', 'y_pos',
            't_startTrial', 'trial_duration', 'trial_duration_exact',
            'task_nr_new',
            'trial_type_new', 'trial_type_nr', 'fixTask', 'withinTaskIndex',
            'x_count', 'fps', 'glasses_binary']]

    subject_columns = [
        # Raw data
        # 'Employment Status', 'chosenAmount', 'chosenDelay',
        # Already analyzed in global
        # 'optionalNote', 'triedChin', 'keptHead',
        # 'num_approvals', 'num_rejections', 'status', 'recorded_date',
        # 'Country of Birth', 'Current Country of Residence', 'max_trial',
        'run_id', 'prolificID',
        'chinFirst', 'choiceTask_amountLeftFirst',
        'webcam_fps', 'webcam_height', 'webcam_width',
        'age', 'gender', 'ethnic', 'degree',
        'First Language', 'Nationality', 'Sex',
        'Student Status', 'employment_status', 'fullTime_binary',
        'sight', 'glasses', 'glasses_binary',
        'vertPosition', 'browser', 'window', 'window_x', 'window_y',
        'eyeshadow', 'masquara', 'eyeliner', 'browliner',
        'Autistic Spectrum Disorder', 'fps']
    selected_columns = np.intersect1d(subject_columns, data_subject.columns)
    data_subject = data_subject[selected_columns]

    save_all_three_datasets(data_et, data_trial, data_subject, path_target)

    return data_et, data_trial, data_subject
