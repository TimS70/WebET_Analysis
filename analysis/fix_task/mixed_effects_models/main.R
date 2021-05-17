root = "C:/Users/User/GitHub/WebET_Analysis"

path_results = file.path(root, 'results', 'plots', 'fix_task')
path_analysis = file.path(root, 'analysis', 'fix_task', 'mixed_effects_models')
setwd(path_analysis)

source('setup.R')

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
		webcam_diag = sqrt(webcam_width**2 + webcam_height**2),
		vertPosition = factor(vertPosition,
							  levels = c('a', 'b', 'c'),
							  labels = c('a', 'b', 'c')))

data_subject %>% 
	dplyr::select(webcam_width, webcam_height) %>%
	table()

data_subject <- data_subject %>% 
	mutate(webcam_high_res = as.numeric(
	webcam_width >= 1280 & webcam_height >=720))

data_subject %>%
	group_by(webcam_high_res) %>%
	dplyr::summarise(
		across(c('offset', 'precision', 'fps'), list(mean = mean, sd = sd)))

data_subject$webcam_fps %>%
	table()

data_trial = data_trial %>%
	merge_by_subject(data_subject, 'window') %>%
	merge_by_subject(data_subject, 'webcam_diag') %>%
	merge_by_subject(data_subject, 'vertPosition') %>%
	merge_by_subject(data_subject, 'ethnic') %>%
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
scatter_matrix_trial(data_trial)
scatter_matrix_subject(data_subject)

# ANOVA
anova_fix_data(data_subject)

get_icc(data=data_trial, outcome='precision') 
get_icc(data=data_trial, outcome='offset') 
get_icc(data=data_trial, outcome='hit_mean') 

control_variables <- paste(
	'withinTaskIndex', 
	'x_pos_c',
	'y_pos_c',
	'window_c',
	# 'fps_c', 
	'webcam_diag',
	'vertPosition',
	'ethnic',
	sep=' + ')

exp_variables <- paste(
	'chin', 
	'glasses_binary',
	sep=' + ')

## Intercept as Outcome	 
grouped = data_subject %>%
    group_by(run_id) %>%
    dplyr::summarise(
    	fps_subject = mean(fps),
    	.groups = 'keep')

data_trial = data_trial %>%
	mutate(y_pos_c = recode(y_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
		   x_pos_c = recode(x_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
		   fps_c = scale(fps),
		   window_c = scale(window),
		   offset_c = scale(offset), 
		   precision_c = scale(precision)) %>%
    merge_by_subject(grouped, 'fps_subject') %>%
    mutate(fps_subject_c = fps - mean(grouped$fps_subject))

lmer_hit_mean <- find_best_model(data=data_trial, outcome='hit_mean',
								 control_variables=control_variables,
								 exp_variables=exp_variables)

lmer_offset <- find_best_model(data=data_trial, outcome='offset',
							   control_variables=control_variables,
 							   exp_variables=exp_variables)

lmer_precision <- find_best_model(data=data_trial, outcome='precision',
								  control_variables=control_variables,
 								  exp_variables=exp_variables)


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
test_assumptions(model=lmer_offset, data=data_trial, outcome='offset')
test_assumptions(model=lmer_precision, data=data_trial, outcome='precision')
test_assumptions(model=lmer_hit_mean, data=data_trial, outcome='hit_mean')
# 
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
