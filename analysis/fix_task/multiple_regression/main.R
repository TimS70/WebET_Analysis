root = "C:/Users/User/GitHub/WebET_Analysis"
setwd(root)
path_results = file.path(root, 'results', 'plots', 'fix_task')
path_analysis = file.path(root, 'analysis', 'fix_task', 'multiple_regression')

source(file.path(path_analysis, 'setup.R'))
get_packages(c('tidyverse', 
			   'car', 
			   'MASS', 
			   'gvlma'))

# Read data
path = file.path(root, 'data', 'fix_task', 'added_var')
data_subject = read.csv(file.path(path, 'data_subject.csv'))
data_trial = read.csv(file.path(path, 'data_trial.csv'))
data_et = read.csv(file.path(path, 'data_et.csv'))

summarize_datasets(data_et, data_trial, data_subject)

# Exclude no outliers
# data_subject <- data_subject %>% 
# 	filter(!run_id %in% data_subject[c(166, 179, 192), 'run_id'])


grouped <- data_trial %>% 
	group_by(run_id) %>%
	dplyr::summarise(hit_mean = mean(hit_mean), 
					 .groups='keep')

data_subject <- data_subject %>%
	mutate(
		ethnic = factor(
			ethnic,
		    levels = c("caucasian", "hispanic", "asian", "black"), 
			labels = c("caucasian", "hispanic", "asian", "black")),
		vert_pos = factor(vertPosition,
						  levels=c('a', 'b', 'c'), 
						  labels=c('a', 'b', 'c'))) %>%
	merge_by_subject(grouped, 'hit_mean')

examine_glasses(data=data_subject, path=file.path(path_results, 'glasses'))

lm_offset <- compare_models(data=data_subject, outcome='offset')
test_assumptions(model=lm_offset, data=data_subject,  
				 path=file.path(root, 'offset'))

# - variance of fps is 23% bigger than would be expected under no 
# multicollinearity

lm_precision <- compare_models(data=data_subject, outcome='precision')
test_assumptions(model=lm_precision, data=data_subject,  
				 path=file.path(root, 'precision'))

lm_hit_mean <- hit_ratio_models(data=data_subject, outcome='hit_mean')
test_assumptions(model=lm_hit_mean, data=data_subject,  
				 path=file.path(root, 'lm_hit_ratio'))


