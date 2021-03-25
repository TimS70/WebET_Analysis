merge_by_subject = function(data, data_source, varName) {
	
    grouped = data_source %>%
        dplyr::select(run_id, varName) %>%
    	distinct()

    if (varName %in% names(data)) {
        data = data %>% dplyr::select(!varName)
    }
    
    data = merge(
        data, 
        data_source %>% dplyr::select(run_id, varName), 
        by='run_id')
    
    return(data)
}