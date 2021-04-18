# https://stackoverflow.com/questions/49904943/run-rmarkdown-with-arguments-on-the-command-line
root = "C:/Users/User/GitHub/WebET_Analysis"
dir.create(file.path(root, 'results', 'html', 'amasino'),
		   showWarnings = FALSE)

rmarkdown::render(
	file.path(root, 'amasino', 'amasino_new_fixation.Rmd'),
	output_file = file.path(root, 'results', 'html', 'amasino',
							'amasino_new_fixation.Rmd'))

# rmarkdown::render(
# 	file.path(root, 'amasino', 
# 			  'bins_and_last_fixation.Rmd'),
# 	output_file = file.path(root, 'results', 'html', 'amasino', 
# 							'bins_and_last_fixation.html'))
