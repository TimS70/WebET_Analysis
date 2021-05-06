path <- file.path(root, 'utils', 'r')
source(file.path(path, 'geom_split_violin.R'))
source(file.path(path, 'merge_by_subject.R'))
source(file.path(path, 'merge_by_index.R'))
source(file.path(path, 'summarize_datasets.R'))
source(file.path(path, 'get_packages.R'))
source(file.path(path, 'remove_runs.R'))
source(file.path(path, 'add_log_k.R'))
source(file.path(path, 'remove_na_et_indices.R'))
source(file.path(path, 'add_x_count.R'))
source(file.path(path, 'identify_bad_choice_runs.R'))
source(file.path(path, 'create_time_bins.R'))
source(file.path(path, 'plot_et_time_bins.R'))
source(file.path(path, 'plot_outcome_variance.R'))
source(file.path(path_analysis, 'check_cat_distribution.R'))
source(file.path(path_analysis, 'predict_option_index.R'))
source(file.path(path_analysis, 'compare_choice_models.R'))
source(file.path(path_analysis, 'simple_slopes.R'))
source(file.path(path_analysis, 'effects.R'))
source(file.path(path_analysis, 'test_clusters.R'))
source(file.path(path_analysis, 'compare_logistic.R'))
source(file.path(path_analysis, 'assumptions.R'))

get_packages(c('broom',
              'car', 
              'colorspace',
			  'DHARMa',
              "effsize",
              'e1071',
              'GGally',
              "ggsignif",
			  'Hmisc',
              'lme4',
              'QuantPsyc',
              "RColorBrewer",
              'reshape2',
              'tidyverse'))