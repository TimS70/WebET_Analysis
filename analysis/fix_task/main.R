root = "C:/Users/User/GitHub/WebET_Analysis"
setwd(root)
path_results = file.path(root, 'results', 'plots', 'fix_task')


source(file.path(root, 'utils', 'r', 'geom_split_violin.R'))
source(file.path(root, 'utils', 'r', 'merge_mean_by_subject.R'))
source(file.path(root, 'utils', 'r', 'merge_mean_by_subject.R'))
source(file.path(root, 'utils', 'r', 'summarize_datasets.R'))
source(file.path(root, 'utils', 'r', 'get_packages.R'))
source(file.path(root, 'utils', 'r', 'remove_runs.R'))
source(file.path(root, 'utils', 'r', 'add_log_k.R'))
source(file.path(root, 'utils', 'r', 'remove_na_et_indices.R'))
source(file.path(root, 'utils', 'r', 'add_x_count.R'))
source(file.path(root, 'utils', 'r', 'plot_outcome_variance.R'))
source(file.path(root, 'analysis', 'fix_task', 'anova_fix_data.R'))
source(file.path(root, 'analysis', 'fix_task', 'scatter_matrix_trial.R'))
source(file.path(root, 'analysis', 'fix_task', 'scatter_matrix_subject.R'))
source(file.path(root, 'analysis', 'fix_task', 'model_comparisons.R'))
source(file.path(root, 'analysis', 'fix_task', 'model_effects.R'))
source(file.path(root, 'analysis', 'fix_task', 'model_robust.R'))

get_packages(c( 'boot',
			    'broom',
			    'car',
			    'compiler',
			    'data.table',
			    'DHARMa',
			    'GGally',
			    'HLMdiag',
			    'Hmisc',
			    'influence.ME', 
			    "ICC",
			    "knitr",
			    'lme4',
			    'lattice',
			    'lme4',
			    "lmerTest", # Erhalte p-Werte
			    'nlme', 
			    'parallel',
			    'reshape',
			    'reshape2',
			    "rsq",
			    'tidyverse',
			    "tinytex"))

# Read data
path = file.path(root, 'data', 'fix_task', 'added_var')

data_subject = read.csv(file.path(path, 'data_subject.csv'))
data_trial = read.csv(file.path(path, 'data_trial.csv'))
data_et = read.csv(file.path(path, 'data_et.csv'))

summarize_datasets(data_et, data_trial, data_subject)

# Modify data
data_subject$ethnic = factor(
	data_subject$ethnic,
	levels = c("caucasian", "hispanic", "asian", "black"), # Faktorstufen
	labels = c("caucasian", "hispanic", "asian", "black"))

data_trial = data_trial %>%
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

data_trial = merge_mean_by_subject(data_trial, data_subject, 'window')
dir.create(file.path(path_results, 'correlations'), showWarnings = FALSE)
scatter_matrix_trial(data_trial)
scatter_matrix_subject(data_subject)

# ANOVA
anova_fix_data(data_subject)

# Models
source(file.path(root, 'analysis', 'fix_task', 'model_comparisons.R'))
source(file.path(root, 'analysis', 'fix_task', 'model_effects.R'))
lmer_offset <- offset_models(data_trial)

# effects
pseudo_r2_l1(data_trial, 'offset')
pseudo_r2_l2(data_trial, 'offset')

# Assumptions
source(file.path(root, 'analysis', 'fix_task', 'assumptions.R'))
test_assumptions(model=lmer_offset, data=data_trial, outcome='offset')


offset_robust(data=data_trial)

