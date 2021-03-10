add_log_k = function(data, re_fit = FALSE) {
	
	if (re_fit == TRUE) {
		run_matlab_script(
			file.path(
				root, 'data_prep', 'fit_k', 'fit_discount_k.m'))
	}
	
    logK <- read.table(file.path(root, 'data', 'choice_task', 'logK.csv'), 
                                 header=TRUE, sep=',')
    if ('logK' %in% names(data)) {
        data = data %>% dplyr::select(!'logK')
    }
    if ('noise' %in% names(data)) {
        data = data %>% dplyr::select(!'noise')
    } 
    
    data = merge(data, logK, by='run_id')
    return(data)
}