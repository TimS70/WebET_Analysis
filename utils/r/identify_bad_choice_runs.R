identify_bad_choice_runs = function(data_subject) {

	runs_biasedChoices = data_subject %>%
	    filter(
	        choseLL>0.98 | choseLL<0.02 |
	        choseTop>0.98 | choseTop<0.02     
	          ) %>%
	    arrange(run_id) %>%
	    dplyr::pull(run_id)
	
	# Missing LogK
	runs_missingLogK = data_subject %>%
	    filter(is.na(logK)) %>%
	    arrange(run_id) %>%
	    dplyr::pull(run_id)
	
	# High noise
	runs_noisy_logK = data_subject %>%
	    filter(noise>40) %>%
	    arrange(run_id) %>%
	    dplyr::pull(run_id)
	
	# Positive logK 
	runs_pos_logK = data_subject %>%
	    filter(logK>0) %>%
	    arrange(run_id) %>%
	    dplyr::pull(run_id)

	
	total_bad_runs = c(
	    runs_biasedChoices,
	    runs_pos_logK,
	    runs_noisy_logK,
	    runs_missingLogK) %>% 
	    sort() %>%
	    unique()
	
	summary = data.frame(
	    reason_for_exclusion = c(    
	        'runs_biasedChoices',
	        'runs_pos_logK',
			'runs_noisy_logK',
			'runs_missingLogK', 
	        'total'),
	    n = c(
	        length(runs_biasedChoices),
	        length(runs_pos_logK),
			length(runs_noisy_logK),
			length(runs_missingLogK), 
	        length(total_bad_runs)
	    )
	)
	
	print(summary)
	
	return(total_bad_runs)
}