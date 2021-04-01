from data_prep.add_variables.data_quality.offset import add_offset, \
    add_hit_ratio, add_n_valid_dots, \
    add_grand_mean_offset
from data_prep.add_variables.data_quality.precision import \
    distance_from_xy_mean_square, \
    aggregate_precision_from_et_data
from utils.combine import merge_by_index, merge_by_subject
from utils.save_data import load_all_three_datasets, save_all_three_datasets
from visualize.eye_tracking import plot_grand_mean


def add_data_quality(max_offset, min_hits_per_dot, path_origin, path_target):
    print('################################### \n'
          'Calculate data quality variables \n'
          '################################### \n')

    data_et, data_trial, data_subject = load_all_three_datasets(path_origin)

    # Offset
    data_et = add_offset(data_et)
    grouped = data_et \
        .groupby(['run_id', 'trial_index'], as_index=False) \
        .agg(offset=('offset', 'mean'),
             offset_px=('offset_px', 'mean'))
    data_trial = merge_by_index(data_trial, grouped,
                                    'offset', 'offset_px')

    data_subject, data_trial = add_grand_mean_offset(data_subject, data_trial,
                                                     data_et)

    grouped = data_et \
        .groupby(['run_id'], as_index=False) \
        .agg(offset=('offset', 'mean'),
             offset_px=('offset_px', 'mean'),
             offset_std=('offset', 'std'),
             offset_px_std=('offset_px', 'std'))
    data_subject = merge_by_subject(data_subject, grouped,
                                    'offset', 'offset_std',
                                    'offset_px', 'offset_px_std')

    plot_grand_mean(data_subject, data_et)

    # Hit-ratio
    data_trial = add_hit_ratio(data_trial, data_et,
                               max_offset=max_offset,
                               min_hit_ratio=min_hits_per_dot)
    data_subject = add_n_valid_dots(data_subject, data_trial)

    # Precision
    data_et = distance_from_xy_mean_square(data_et)
    data_trial = aggregate_precision_from_et_data(data_trial, data_et)

    grouped = data_trial \
        .groupby(['run_id'], as_index=False) \
        .agg(precision=('precision', 'mean'),
             precision_px=('precision_px', 'mean'))
    data_subject = merge_by_subject(data_subject, grouped,
                                    'precision', 'precision_px')

    save_all_three_datasets(data_et, data_trial, data_subject, path_target)
