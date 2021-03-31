from utils.combine import merge_by_index
from utils.save_data import load_all_three_datasets, save_all_three_datasets


def load_choice_data(path_origin, path_target):
    print('################################### \n'
          'Create choice data \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(path_origin)

    data_trial = data_trial.loc[
        data_trial['trial_type'] == 'eyetracking-choice', [
            'run_id', 'prolificID', 'chinFirst',
            'task_nr',
            'trial_index', 'trial_type', 'withinTaskIndex',
            'choiceTask_amountLeftFirst',
            'option_topLeft', 'option_bottomLeft',
            'option_topRight', 'option_bottomRight',
            'key_press', 'trial_duration_exact',
            'window_width', 'window_height',
            'fps']]

    data_et = merge_by_index(data_et, data_trial, 'trial_type')
    data_et = merge_by_index(data_et, data_trial, 'withinTaskIndex')

    data_et = data_et[data_et['trial_type'] == 'eyetracking-choice'] \
        .drop(columns=['trial_type'])
    data_et = data_et[['run_id', 'trial_index', 'withinTaskIndex', 'x', 'y',
                       't_task']]

    data_subject = data_subject[[
        # Raw data
        # 'Employment Status', 'chosenAmount', 'chosenDelay',
        # Already analyzed in global
        # 'optionalNote', 'num_approvals', 'num_rejections', 'status',
        # 'recorded_date', 'max_trial', 'triedChin', 'keptHead',
        # Already in fix_task
        # 'eyeshadow', 'masquara', 'eyeliner', 'browliner',
        # 'sight', 'glasses', 'glasses_binary',
        # 'webcam_fps', 'webcam_height', 'webcam_width',
        # 'browser', 'vertPosition',
        'run_id', 'prolificID', 'chinFirst', 'choiceTask_amountLeftFirst',
        'age', 'gender', 'ethnic',
        'degree',
        'Country of Birth', 'Current Country of Residence',
        'First Language', 'Nationality', 'Sex',
        'Autistic Spectrum Disorder', 'fps',
        'Student Status', 'employment_status', 'fullTime_binary']]

    save_all_three_datasets(data_et, data_trial, data_subject, path_target)
