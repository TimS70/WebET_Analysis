root = "C:/Users/User/GitHub/WebET_Analysis"
setwd(root)
path_results = file.path(root, 'results', 'plots', 'choice_task')
path_analysis = file.path(root, 'analysis', 'choice_task', 'logistic_regression')

source(file.path(path_analysis, 'setup.R'))
get_packages(c('tidyverse', 
			   'broom'))
# Read data
path = file.path(root, 'data', 'choice_task', 'cleaned')

data_subject = read.csv(file.path(path, 'data_subject.csv'))
data_trial = read.csv(file.path(path, 'data_trial.csv'))
data_et = read.csv(file.path(path, 'data_et.csv'))

summarize_datasets(data_et, data_trial, data_subject)

# Exclude no outliers
# data_subject <- data_subject %>% 
# 	filter(!run_id %in% data_subject[c(166, 179, 192), 'run_id'])

# Some outliers were found but they do not have any atypical properties 
data_subject %>%
	filter(run_id %in% data_subject[c(15, 34), 'run_id']) %>%
	dplyr::select(age, ethnic, fps, window, offset, precision, n_valid_dots, 
				  choice_rt, choseLL, choseTop, attributeIndex, optionIndex, 
				  payneIndex, logK, noise) %>%
	t()

# Modify data
data_subject <- data_subject %>%
	mutate(
		ethnic = factor(ethnic,
			levels = c("caucasian", "hispanic", "asian", "black"), # Faktorstufen
			labels = c("caucasian", "hispanic", "asian", "black")),
		optionIndex_2 = optionIndex**2)

glm_choice <- compare_models(data=data_subject)

source(file.path(path_analysis, 'setup.R'))
test_assumptions(model=glm_choice, data=data_subject, 
				 path=file.path(path_results, 'assumptions', 'logistic'))

