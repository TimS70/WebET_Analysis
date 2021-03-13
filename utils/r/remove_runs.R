remove_runs = function(data_raw, exclude_runs) {

    data = data_raw %>%
        filter(!(run_id %in% exclude_runs))
    
	summary = data.frame(
	    names = c(
	    	'name', 
	        'Raw length',
	        'Raw runs',
	        'Cleaned length',
	        'Cleaned runs'
	    ),
	    n = c(
	    	deparse(substitute(data_raw)),
	        nrow(data_raw),
	        length(unique(data_raw$run_id)),
	        nrow(data),
	        length(unique(data$run_id))
	    )
	)
	    
    print(summary)
    
	
    return(data)
}