scatter_matrix_trial <- function(data_trial) {
	my_plot <- ggpairs(data_trial,
		columns = c('withinTaskIndex', 'chinFirst', 'window', 'fps', 
					'x_pos', 'y_pos', 'glasses_binary', 'chin', 'hit_mean',
					'precision', 'offset'), 
		upper = list(continuous = wrap("cor", size = 2)),
		lower = list(continuous = wrap("smooth", alpha = 0.3, size=0.01)),
		progress = F) +
	theme_bw()
	
	print(my_plot)

	ggsave(file.path(path_results, 'correlations_trial.png'),
		   width=5.5, height=5)
}