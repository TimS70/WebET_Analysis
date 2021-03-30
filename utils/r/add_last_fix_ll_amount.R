add_last_fix_ll_amount = function(data_trial, data_et) {
	
    grouped_last_coordinate = data_et %>%
    	filter(aoi %in% c('TL', 'TR', 'BL', 'BR')) %>%
        dplyr::group_by(run_id, trial_index) %>%
        slice(n()) %>%
	    mutate(last_fix_ll = factor(as.numeric(
	              (aoi %in% c('TL', 'TR') & LL_top==1) |
	              (aoi %in% c('BL', 'BR') & LL_top==0))),
	           last_fix_amount = factor(as.numeric(
	              (aoi %in% c('TL', 'BL') & amountLeft==1) |
	              (aoi %in% c('TR', 'BR') & amountLeft==0))))
    
    data_trial = data_trial %>%
    	merge_by_index(grouped_last_coordinate, 'last_fix_ll') %>%
    	merge_by_index(grouped_last_coordinate, 'last_fix_amount')
    
    return(data_trial)
}