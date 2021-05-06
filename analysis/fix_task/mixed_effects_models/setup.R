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

get_packages(c( 'brms',
				'boot',
				'boxcoxmix',
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
				'RcppParallel', 
			    "rsq",
			    'tidyverse',
			    "tinytex"))