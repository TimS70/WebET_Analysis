root = "C:/Users/schne/Documents/github/WebET_Analysis"
setwd(root)

path_analysis <- file.path(root, 'analysis', 'choice_task', 'mixed_effects_models')
path_results = file.path(root, 'results', 'plots', 'choice_task')

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
source(file.path(path_analysis, 'compare_models.R'))
source(file.path(path_analysis, 'simple_slopes.R'))
source(file.path(path_analysis, 'effects.R'))
source(file.path(path_analysis, 'test_clusters.R'))
source(file.path(path_analysis, 'assumptions.R'))

library('broom')
library('car')
library('colorspace')
library('dplyr')
library('DHARMa')
library("effsize")
library('e1071')
library('GGally')
library("ggsignif")
library('Hmisc')
library('lme4')
library('QuantPsyc')
library("RColorBrewer")
library('reshape2')
library('tidyverse')

path <- file.path(root, 'data', 'choice_task', 'cleaned')
data_subject <- read.csv(file.path(path, 'data_subject.csv'))
data_trial <- read.csv(file.path(path, 'data_trial.csv'))
data_et <- read.csv(file.path(path, 'data_et.csv'))

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

# compare_logistic(data_subject)

glmer_choice <- compare_choice_models(
    data=data_clean,
    data_subject=data_subject,
	get_ci=FALSE
)

test_clusters(model=glmer_choice, data=data_clean)

glmer_sd_ul <- simple_slopes(data=data_clean, model=glmer_choice, upper=TRUE)
glmer_sd_ll <- simple_slopes(data=data_clean, model=glmer_choice, upper=FALSE)

odds_ratio(model=glmer_choice, data=data_clean) 

# Test_Assumptions
test_assumptions(
  model=glmer_choice, data=data_clean,
  path=file.path('results', 'plots', 'choice_task', 'assumptions'))

