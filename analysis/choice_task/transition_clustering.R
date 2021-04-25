# setup
root = "C:/Users/User/GitHub/WebET_Analysis"
setwd(root)
path_results = file.path(root, 'results', 'plots', 'choice_task')

source(file.path(root, 'utils', 'r', 'geom_split_violin.R'))
source(file.path(root, 'utils', 'r', 'merge_by_subject.R'))
source(file.path(root, 'utils', 'r', 'merge_by_index.R'))
source(file.path(root, 'utils', 'r', 'summarize_datasets.R'))
source(file.path(root, 'utils', 'r', 'get_packages.R'))
source(file.path(root, 'utils', 'r', 'remove_runs.R'))
source(file.path(root, 'utils', 'r', 'add_log_k.R'))
source(file.path(root, 'utils', 'r', 'remove_na_et_indices.R'))
source(file.path(root, 'utils', 'r', 'add_x_count.R'))
source(file.path(root, 'utils', 'r', 'identify_bad_choice_runs.R'))
source(file.path(root, 'utils', 'r', 'create_time_bins.R'))
source(file.path(root, 'utils', 'r', 'plot_et_time_bins.R'))
source(file.path(root, 'utils', 'r', 'plot_outcome_variance.R'))

source(file.path(root, 'analysis', 'choice_task', 'fit_clusters.R'))
source(file.path(root, 'analysis', 'choice_task', 'plot_transition_strength.R'))

get_packages(c(
	'apaTables',
	'broom',
	'car', 
	'colorspace',
	"effsize",
	'e1071',
	'GGally',
	'ggplot2',
	"ggsignif",
	'Hmisc',
	'lme4',
	'QuantPsyc',
	"RColorBrewer",
	'reshape2',
	'tidyverse'))

# Load data
path = file.path(root, 'data', 'choice_task', 'cleaned')
data_subject = read.csv(file.path(path, 'data_subject.csv'))
data_trial = read.csv(file.path(path, 'data_trial.csv'))
data_et = read.csv(file.path(path, 'data_et.csv'))

summarize_datasets(data_et, data_trial, data_subject)

data_trial$rt_c = scale(data_trial$trial_duration_exact)

# The two cluster solution fits best
model_comparison = fit_clusters(data_trial)

plot_transition_strength(data=data_trial,
						 cluster=1, 
						 parralel_distance=0.01, 
						 cluster_name = 'cluster2',
						 strength_factor=1.5,
						 cutoff=0,
						 undirected=TRUE,
						 title = 'Gaze transitions of cluster 1 trials')
ggsave(file.path(path_results, 'et', 'transitions_cluster_1.png'), 
	   width=5.5, height=5)


plot_transition_strength(data=data_trial,
						 cluster=2, 
						 parralel_distance=0.01, 
						 cluster_name = 'cluster2',
						 strength_factor=1.5,
						 cutoff=0,
						 undirected=TRUE,
						 title = 'Gaze transitions of cluster 2 trials')
ggsave(file.path(path_results, 'et', 'transitions_cluster_2.png'), 
	   width=5.5, height=5)