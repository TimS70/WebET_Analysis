setwd <- "C:/Users/schne/Documents/github/WebET_Analysis"
root <- "C:/Users/schne/Documents/github/WebET_Analysis"
path_results <- file.path(root, 'results', 'plots', 'fix_task')
path_analysis <- file.path(root, 'analysis', 'fix_task', 'multiple_regression')

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

get_packages(c('tidyverse',
			   'car',
			   'MASS',
			   'gvlma'))

# Read data
path <- file.path('data', 'fix_task', 'added_var')
data_subject <- read.csv(file.path(path, 'data_subject.csv'))
data_trial <- read.csv(file.path(path, 'data_trial.csv'))
data_et <- read.csv(file.path(path, 'data_et.csv'))

summarize_datasets(data_et, data_trial, data_subject)

data_subject <- prep_data_subject(
	data_subject=data_subject,
	data_trial=data_trial
)

# inspect_outliers(data_subject=data_subject, 
# 				 data_et=data_et)

predict_validation(data=data_subject)

examine_glasses(data=data_subject, path=file.path(path_results, 'glasses'))

lm_offset <- compare_models(data=data_subject, outcome='offset')
test_assumptions(model=lm_offset, data=data_subject,  
				 path=file.path(root, 'offset'))

lm_grand_offset <- grand_offset_model(data=data_subject)

# - variance of fps is 23% bigger than would be expected under no
# multicollinearity

lm_precision <- compare_models(data=data_subject, outcome='precision')
test_assumptions(model=lm_precision, data=data_subject,  
				 path=file.path(root, 'precision'))

lm_hit_mean <- hit_ratio_models(data=data_subject, outcome='hit_mean')
test_assumptions(model=lm_hit_mean, data=data_subject,  
				 path=file.path(root, 'lm_hit_ratio'))
