root = "C:/Users/User/GitHub/WebET_Analysis"
setwd(root)
path_analysis <- file.path(root, 'analysis', 'choice_task',
						   'mixed_effects_models')
path_results = file.path(root, 'results', 'plots', 'choice_task')

source(file.path(path_analysis, 'setup.R'))

path = file.path(root, 'data', 'choice_task', 'cleaned')
data_subject = read.csv(file.path(path, 'data_subject.csv'))
data_trial = read.csv(file.path(path, 'data_trial.csv'))
data_et = read.csv(file.path(path, 'data_et.csv'))

summarize_datasets(data_et, data_trial, data_subject)

data_trial <- data_trial %>%
	mutate(rt_c = scale(trial_duration_exact))

plot_outcome_variance(data_trial, 'choseLL')
ggsave(file.path(path_results, 'runs_vs_choseLL.png'))

check_cat_distribution(data=data_trial)

predict_option_index(data=data_trial)

data_clean <- data_trial %>%
	mutate(rt_c = scale(trial_duration_exact), 
		   optionIndex_2 = optionIndex^2) %>%
   	filter(!is.na(attributeIndex) &
   		   !is.na(payneIndex) &
		   !is.na(optionIndex))

compare_logistic(data_subject)

glmer_choice <- compare_choice_models(data=data_clean,
									  data_subject=data_subject)

test_clusters(model=glmer_choice, data=data_clean)

glmer_sd_ul <- simple_slopes(data=data_clean, model=glmer_choice, upper=TRUE)
glmer_sd_ll <- simple_slopes(data=data_clean, model=glmer_choice, upper=FALSE)

odds_ratio(model=glmer_choice, data=data_clean) 

# Test_Assumptions
test_assumptions(model=glmer_choice, data=data_clean)
