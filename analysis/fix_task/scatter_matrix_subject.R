scatter_matrix_subject <- function(data_subject) {
	my_plot <- ggpairs(data_subject %>% dplyr::select(
		glasses_binary, window, fps, 
		age, ethnic, hit_ratio,
		offset, precision),
		progress = F) 
	
	print(my_plot)
	
	ggsave(file.path(path_results, 'correlations_participant.png'),
		   width=5.5, height=5)
}