add_x_count = function(data_trial, data_et) {
	grouped = data_et %>% group_by(run_id, trial_index) %>%
		dplyr::summarise(x_count = n(), .groups='keep') %>%
		dplyr::select(run_id, trial_index, x_count)

    if ('x_count' %in% names(data_trial)) {
        data_trial = data_trial %>% dplyr::select(!x_count)
    }
	
	data_trial = merge(data_trial, grouped, by=c('run_id', 'trial_index'))
	
	return(data_trial)
}