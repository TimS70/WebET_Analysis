# https://stackoverflow.com/questions/49904943/run-rmarkdown-with-arguments-on-the-command-line
root = "C:/Users/User/GitHub/WebET_Analysis"
dir.create(
	file.path(root, 'results', 'html'),
	showWarnings = FALSE)

rmarkdown::render(
	file.path(root, 'analysis', 'choice_task', 'amasino_replication.Rmd'),
	output_file = file.path(root, 'results', 'html',
							'amasino_replication.html'))

rmarkdown::render(
	file.path(root, 'analysis', 'choice_task', 
			  'bins_and_last_fixation.Rmd'),
	output_file = file.path(root, 'results', 'html',
							'bins_and_last_fixation.html'))

rmarkdown::render(
	file.path(root, 'analysis', 'choice_task', 'models_choice.Rmd'), 
	output_file = file.path(root, 'results', 'html', 
							'models_choice.html'))

# rmarkdown::render(
# 	file.path(root, 'analysis', 'choice_task', 'models_cluster_corrected.Rmd'), 
# 	output_file = file.path(root, 'results', 'html', 
# 							'models_cluster_corrected.html'))

rmarkdown::render(
	file.path(root, 'analysis', 'fix_task', 'models_fix_offset.Rmd'), 
	output_file = file.path(root, 'results', 'html', 
							'models_fix_offset.html'))

rmarkdown::render(
	file.path(root, 'analysis', 'fix_task', 'models_fix_precision.Rmd'), 
	output_file = file.path(root, 'results', 'html', 
							'models_fix_precision.html'))
