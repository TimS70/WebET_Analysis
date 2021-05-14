source(file.path(root, 'utils', 'r', 'merge_by_subject.R'))

prep_data_subject <- function(data_subject, data_trial) {
	
	grouped <- data_trial %>% 
	group_by(run_id) %>%
	dplyr::summarise(hit_mean = mean(hit_mean), 
					 .groups='keep')

	data_subject <- data_subject %>%
		mutate(
			ethnic = factor(
				ethnic,
			    levels = c("caucasian", "hispanic", "asian", "black"), 
				labels = c("caucasian", "hispanic", "asian", "black")),
			vert_pos = factor(vertPosition,
							  levels=c('a', 'b', 'c'), 
							  labels=c('a', 'b', 'c')),
			webcam_diag = sqrt(webcam_width**2 + webcam_height**2))  %>%
		merge_by_subject(grouped, 'hit_mean')
	
	return(data_subject)
}