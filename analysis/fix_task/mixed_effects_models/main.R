setwd('C:/Users/schne/Documents/github/WebET_Analysis')

library("boot")
library("broom")
library("car")
library("compiler")
library("data.table")
library("GGally")
library("Hmisc")
library("influence.ME")
library("ICC")
library("knitr")
library("lme4")
library("lattice")
library("lme4")
library("lmerTest") # Erhalte p-Werte
library("MASS")
library("nlme")
library("parallel")
library("reshape")
library("reshape2")
library("RcppParallel")
library("rsq")
library("tidyverse")
library("tinytex")

root <- getwd()
path_results = file.path(root, 'results', 'plots', 'fix_task')
path_analysis = file.path(root, 'analysis', 'fix_task', 'mixed_effects_models')

source(file.path(root, 'utils', 'r', 'geom_split_violin.R'))
source(file.path(root, 'utils', 'r', 'merge_by_subject.R'))
source(file.path(root, 'utils', 'r', 'summarize_datasets.R'))
source(file.path(root, 'utils', 'r', 'get_packages.R'))
source(file.path(root, 'utils', 'r', 'remove_runs.R'))
source(file.path(root, 'utils', 'r', 'add_log_k.R'))
source(file.path(root, 'utils', 'r', 'remove_na_et_indices.R'))
source(file.path(root, 'utils', 'r', 'add_x_count.R'))
source(file.path(root, 'utils', 'r', 'plot_outcome_variance.R'))
source(file.path(path_analysis, 'anova_fix_data.R'))
source(file.path(path_analysis, 'scatter_matrix_trial.R'))
source(file.path(path_analysis, 'scatter_matrix_subject.R'))
source(file.path(path_analysis, 'compare.R'))
source(file.path(path_analysis, 'effects.R'))
source(file.path(path_analysis, 'robust.R'))
source(file.path(path_analysis, 'assumptions.R'))
source(file.path(path_analysis, 'transformation.R'))
source(file.path(path_analysis, 'icc.R'))
source(file.path(path_analysis, 'prep_data.R'))

# Read data
path <- file.path(root, 'data', 'fix_task', 'added_var')

data_subject <- read.csv(file.path(path, 'data_subject.csv'))
data_trial <- read.csv(file.path(path, 'data_trial.csv'))
data_et <- read.csv(file.path(path, 'data_et.csv'))

summarize_datasets(data_et, data_trial, data_subject)

data_subject <- prep_subject_data(data_subject=data_subject)
data_trial <- prep_trial_data(data_subject=data_subject, data_trial=data_trial)

# Visual inspection
# for (var in c('offset', 'precision', 'hit_mean')) {
# 	plot_outcome_variance(data_trial, var)
# 	ggsave(file.path(path_results, 'MLA', paste0('runs_vs_', var, '.png')), 
# 		   width=5.5, height=5)
# }
# 
# dir.create(file.path(path_results, 'correlations'), showWarnings = FALSE)
# scatter_matrix_trial(data_trial)
# scatter_matrix_subject(data_subject)

# ANOVA
# anova_fix_data(data_subject)

get_icc(data=data_trial, outcome='hit_mean')
get_icc(data=data_trial, outcome='offset')
get_icc(data=data_trial, outcome='precision')

lmer_hit_mean <- hit_ratio_models(data=data_trial, get_ci=FALSE)
lmer_offset <- offset_models(data=data_trial, get_ci=FALSE)
lmer_offset <- grand_offset_models(data=data_trial, get_ci=FALSE)
lmer_precision <- precision_models(data=data_trial, get_ci=FALSE)

# effects
# pseudo_r2_l1(data_trial, 'offset')
# pseudo_r2_l2(data_trial, 'offset')
# 
# pseudo_r2_l1(data_trial, 'precision')
# pseudo_r2_l2(data_trial, 'precision')
# 
# pseudo_r2_l1(data_trial, 'hit_mean')
# pseudo_r2_l2(data_trial, 'hit_mean')

# Assumptions
test_assumptions(model=lmer_hit_mean, data=data_trial, outcome='hit_mean',
                 path=file.path('results', 'plots', 'fix_task', 'assumptions', 
                           'hit_mean'))
test_assumptions(model=lmer_offset, data=data_trial, outcome='offset',
                 path=file.path('results', 'plots', 'fix_task', 'assumptions', 
                                'offset'))
test_assumptions(model=lmer_precision, data=data_trial, outcome='precision',
                 path=file.path('results', 'plots', 'fix_task', 'assumptions', 
                                'precision'))

# lmer_offset_log <- compare_models(data=data_trial, outcome='offset_log',
#                                control_variables=control_variables,
#                                exp_variables=exp_variables)
# 
# lmer_precision_log <- compare_models(data=data_trial, outcome='precision_log',
#                                   control_variables=control_variables,
#                                   exp_variables=exp_variables)
# test_assumptions(model=lmer_offset_log, data=data_trial, 
#                  outcome='offset_log')
# test_assumptions(model=lmer_precision_log, data=data_trial, 
#                  outcome='precision_log')

transform_model(data=data_trial, model=lmer_offset, outcome='offset')
transform_model(data=data_trial, model=lmer_precision, outcome='precision')
transform_model(data=data_trial, model=lmer_hit_mean, outcome='hit_mean')

data_trial = data_trial %>%
	mutate(offset_log = log(offset),
		   precision_log = log(precision))
		   
lmer_offset <- find_best_model(data=data_trial, outcome='offset_log',
							   control_variables=control_variables,
 							   exp_variables=exp_variables)

lmer_precision <- find_best_model(data=data_trial, outcome='precision_log',
								  control_variables=control_variables,
 								  exp_variables=exp_variables)

sessionInfo()
