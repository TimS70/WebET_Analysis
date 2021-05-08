root = "C:/Users/User/GitHub/WebET_Analysis"
setwd(root)
path_results = file.path(root, 'results', 'plots', 'fix_task')
path_analysis = file.path(root, 'analysis', 'fix_task', 'multiple_regression')

source(file.path(path_analysis, 'setup.R'))

# Read data
path = file.path(root, 'data', 'fix_task', 'added_var')
data_subject = read.csv(file.path(path, 'data_subject.csv'))
data_trial = read.csv(file.path(path, 'data_trial.csv'))
data_et = read.csv(file.path(path, 'data_et.csv'))

summarize_datasets(data_et, data_trial, data_subject)

data_subject <- prep_data_subject(data_subject=data_subject, 
				  data_trial=data_trial)

inspect_outliers(data_subject=data_subject, 
				 data_et=data_et)

predict_validation(data=data_subject)

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


