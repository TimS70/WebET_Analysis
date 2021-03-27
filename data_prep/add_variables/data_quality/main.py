import os

from data_prep.add_variables.data_quality.offset import add_offset, add_hit_ratio, add_n_valid_dots, \
    add_grand_mean_offset
from data_prep.add_variables.data_quality.precision import distance_from_xy_mean_square, \
    aggregate_precision_from_et_data
from utils.combine_frames import merge_mean_by_index, merge_mean_by_subject
from utils.save_data import load_all_three_datasets, save_all_three_datasets


def add_data_quality():
    print('################################### \n'
          'Calculate data quality variables \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(
        os.path.join('data', 'fix_task', 'cleaned'))

    # Offset
    data_et = add_offset(data_et)
    data_trial = merge_mean_by_index(data_trial, data_et,
                                     'offset', 'offset_px')

    # Hit-ratio
    data_trial = add_hit_ratio(data_trial, data_et,
                               max_offset=0.13, min_hit_ratio=0.8)

    data_trial = add_grand_mean_offset(data_trial)

    data_subject = add_n_valid_dots(data_subject, data_trial)

    data_subject = merge_mean_by_subject(data_subject, data_trial,
                                         'offset', 'offset_px')

    # Precision
    data_et = distance_from_xy_mean_square(data_et)
    data_trial = aggregate_precision_from_et_data(data_trial, data_et)
    data_subject = merge_mean_by_subject(data_subject, data_trial,
                                         'precision', 'precision_px')

    save_all_three_datasets(data_et, data_trial, data_subject,
                            os.path.join('data', 'fix_task', 'added_var'))
