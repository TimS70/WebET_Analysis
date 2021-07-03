# setup
path_results <- file.path('results', 'plots', 'choice_task')
source(file.path('utils', 'r', 'geom_split_violin.R'))
source(file.path('utils', 'r', 'merge_by_subject.R'))
source(file.path('utils', 'r', 'merge_by_index.R'))
source(file.path('utils', 'r', 'summarize_datasets.R'))
source(file.path('utils', 'r', 'get_packages.R'))
source(file.path('utils', 'r', 'remove_runs.R'))
source(file.path('utils', 'r', 'add_log_k.R'))
source(file.path('utils', 'r', 'remove_na_et_indices.R'))
source(file.path('utils', 'r', 'add_x_count.R'))
source(file.path('utils', 'r', 'identify_bad_choice_runs.R'))
source(file.path('utils', 'r', 'create_time_bins.R'))
source(file.path('utils', 'r', 'plot_et_time_bins.R'))
source(file.path('analysis', 'choice_task', 'gaze_transitions', 'add_clusters.R'))
source(file.path('analysis', 'choice_task', 'gaze_transitions', 'compare_models.R'))
source(file.path('analysis', 'choice_task', 'gaze_transitions', 'plot_transition_strength.R'))

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
path <- file.path('data', 'choice_task', 'cleaned')
data_subject <- read.csv(file.path(path, 'data_subject.csv'))
data_trial <- read.csv(file.path(path, 'data_trial.csv'))
data_et <- read.csv(file.path(path, 'data_et.csv'))

summarize_datasets(data_et, data_trial, data_subject)

print(names(data_subject))

data_subject$cluster_2 <- add_clusters(
	data=data_subject,
	n_cluster=2
)

data_subject$cluster_3 <- add_clusters(
	data=data_subject,
	n_cluster=3
)

data_subject$cluster_4 <- add_clusters(
	data=data_subject,
	n_cluster=4
)

data_trial <- data_trial %>%
	merge(
		data_subject[ , c('run_id', 'cluster_2', 'cluster_3', 'cluster_4')],
	    by='run_id')

glmer_cluster_2 <- compare_models(data=data_trial, get_ci=FALSE)

print(summary(glmer_cluster_2))
# print(confint(glmer_cluster_2, method="boot", n=500))

table(data_subject$cluster2)
table(data_subject$cluster3)

data_subject %>%
	filter(cluster3==2) %>%
	dplyr::select(run_id, cluster2, cluster3)

scatter_matrix(data=data_subject, 
			   path=file.path(path_results, 'et', 'cluster_matrix.png'))

plot_transition_strength(data=data_subject,
						 cluster=1, 
						 parralel_distance=0.01, 
						 cluster_name = 'cluster2',
						 strength_factor=1.5,
						 cutoff=0,
						 undirected=TRUE,
						 title = '')
ggsave(file.path(path_results, 'et', 'transitions_cluster_1.png'), 
	   width=5.5, height=5)

plot_transition_strength(data=data_subject,
						 cluster=2, 
						 parralel_distance=0.01, 
						 cluster_name = 'cluster2',
						 strength_factor=1.5,
						 cutoff=0,
						 undirected=TRUE,
						 title = '')
ggsave(file.path(path_results, 'et', 'transitions_cluster_2.png'),
	   width=5.5, height=5)