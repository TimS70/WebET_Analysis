root = "C:/Users/User/GitHub/WebET_Analysis"
source(file.path(root, 'utils', 'r', 'get_packages.R'))
source(file.path(root, 'utils', 'r', 'summarize_datasets.R'))

# https://dstanley4.github.io/apaTables/articles/apaTables.html#ezanova-and-apatables-repeated-measures-anova
get_packages(c('apaTables', 'tidyverse'))

# Load data
path = file.path(root, 'data', 'fix_task', 'added_var')
data_subject = read.csv(file.path(path, 'data_subject.csv'))
data_trial = read.csv(file.path(path, 'data_trial.csv'))
data_et = read.csv(file.path(path, 'data_et.csv'))
summarize_datasets(data_et, data_trial, data_subject)

# Glasses
path = file.path(root, 'results', 'tables', 'apa')
dir.create(path, showWarnings = FALSE)
outcomes = c('offset', 'precision', 'fps')

for (predictor in c('sight', 'glasses')) {
	for (i in c(1:length(outcomes))) {
		print(i)
		print(outcomes[i])
		lm_output <- lm(paste(outcome, predictor, sep = ' ~ '), 
						data = data_subject)
		table = apa.aov.table(lm_output, 
							  filename = file.path(path, paste('aov_',
							  								 outcomes[i], 
							  								 '_vs_', predictor, 
							  								 '.doc', sep = '')), 
							  table.number = i)
		print(table)
	}
}
