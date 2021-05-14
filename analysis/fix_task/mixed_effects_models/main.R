root = "C:/Users/User/GitHub/WebET_Analysis"
setwd(root)
path_results = file.path(root, 'results', 'plots', 'fix_task')
path_analysis = file.path(root, 'analysis', 'fix_task', 'mixed_effects_models')

source(file.path(path_analysis, 'setup.R'))

# Read data
path = file.path(root, 'data', 'fix_task', 'added_var')

data_subject = read.csv(file.path(path, 'data_subject.csv'))
data_trial = read.csv(file.path(path, 'data_trial.csv'))
data_et = read.csv(file.path(path, 'data_et.csv'))

summarize_datasets(data_et, data_trial, data_subject)

# Modify data
data_subject <- data_subject %>%
	mutate(
		ethnic = factor(
			ethnic,
			levels = c("caucasian", "hispanic", "asian", "black"), # Faktorstufen
			labels = c("caucasian", "hispanic", "asian", "black")),
		webcam_diag = sqrt(webcam_width**2 + webcam_height**2))


data_trial = data_trial %>%
	merge_by_subject(data_subject, 'window') %>%
	merge_by_subject(data_subject, 'webcam_diag') %>%
	mutate(y_pos_c = recode(y_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
		   x_pos_c = recode(x_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
		   fps_c = scale(fps),
		   window_c = scale(window))

# Visual inspection
for (var in c('offset', 'precision', 'hit_mean')) {
	plot_outcome_variance(data_trial, var)
	ggsave(file.path(path_results, 'MLA', paste0('runs_vs_', var, '.png')), 
		   width=5.5, height=5)
}

dir.create(file.path(path_results, 'correlations'), showWarnings = FALSE)
# scatter_matrix_trial(data_trial)
# scatter_matrix_subject(data_subject)

# ANOVA
anova_fix_data(data_subject)

get_icc(data=data_trial, outcome='precision') 
get_icc(data=data_trial, outcome='offset') 
get_icc(data=data_trial, outcome='hit_mean') 

lmer_precision <- find_best_model(data=data_trial, outcome='precision')
lmer_offset <- find_best_model(data=data_trial, outcome='offset')
lmer_hit_mean <- find_best_model(data=data_trial, outcome='hit_mean')

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
# test_assumptions(model=lmer_offset, data=data_trial, outcome='offset')
# test_assumptions(model=lmer_precision, data=data_trial, outcome='precision')
# test_assumptions(model=lmer_hit_mean, data=data_trial, outcome='hit_mean')
# 
# transform_model(data=data_trial, model=lmer_offset, outcome='offset')
# transform_model(data=data_trial, model=lmer_precision, outcome='precision')
# transform_model(data=data_trial, model=lmer_hit_mean, outcome='hit_mean')

# brm_0 <- find_brm_models(data=data_trial, outcome='offset')
# offset_robust(data=data_trial)

sessionInfo()
