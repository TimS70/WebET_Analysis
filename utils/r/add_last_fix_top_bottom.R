add_last_fix_top_bottom = function(data_trial, data_et) {
	
    grouped_last_coordinate = data_et %>%
    	filter(aoi %in% c('TL', 'TR', 'BL', 'BR')) %>%
        dplyr::group_by(run_id, trial_index) %>%
        slice(n()) %>%
    	mutate(
    		last_fix_top = factor(as.numeric(aoi %in% c('TL', 'TR')),
    							 c('1', '0')),
        	last_fix_bottom = factor(as.numeric(aoi %in% c('BL', 'BR')),
        							c('1', '0')))
    
    data_trial = data_trial %>%
    	merge_by_index(grouped_last_coordinate, 'last_fix_top') %>%
    	merge_by_index(grouped_last_coordinate, 'last_fix_bottom')
    
    return(data_trial)
}