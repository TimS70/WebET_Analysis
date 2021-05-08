source(file.path(root, 'utils', 'r', 'geom_split_violin.R'))
source(file.path(root, 'utils', 'r', 'merge_by_subject.R'))
source(file.path(root, 'utils', 'r', 'summarize_datasets.R'))
source(file.path(root, 'utils', 'r', 'get_packages.R'))
source(file.path(root, 'utils', 'r', 'remove_runs.R'))
source(file.path(root, 'utils', 'r', 'add_log_k.R'))
source(file.path(root, 'utils', 'r', 'remove_na_et_indices.R'))
source(file.path(root, 'utils', 'r', 'add_x_count.R'))
source(file.path(path_analysis, 'compare_models.R'))
source(file.path(path_analysis, 'assumptions.R'))
source(file.path(path_analysis, 'glasses.R'))
source(file.path(path_analysis, 'inspect_outliers.R'))
source(file.path(path_analysis, 'prep_data_subject.R'))
source(file.path(path_analysis, 'predict_validation.R'))

output_packages <- get_packages(c('tidyverse', 
								   'car', 
								   'MASS', 
								   'gvlma'))

print(output_packages)