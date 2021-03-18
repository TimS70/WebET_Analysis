merge_by_index = function(data, data_source, varName) {
	
    grouped = data_source %>%
        dplyr::select(run_id, trial_index, varName) %>%
    	distinct()

    if (varName %in% names(data)) {
        data = data %>% dplyr::select(!varName)
    }
    
    data = merge(
        data, 
        data_source %>% dplyr::select(run_id, trial_index, varName), 
        by=c('run_id', 'trial_index'))
    
    return(data)
}