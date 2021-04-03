plot_outcome_variance = function(data_trial, outcome) {

	grouped = data_trial %>% 
	    group_by(run_id) %>%
	    dplyr::summarise(
	        n = n(),
	        mean = mean(!!as.symbol(outcome)),
	        sd = sd(!!as.symbol(outcome)),
	        .groups='keep') %>%
		mutate(sem = sd / sqrt(n)) %>%
	    arrange(run_id, mean)

	plot = ggplot(grouped, aes(factor(run_id), mean)) + 
	    geom_pointrange(aes(ymin=mean-1.96*sem, 
	                        ymax=mean+1.96*sem)) +
	    xlab('run_id') +
	    ylab(outcome) + 
	    theme(axis.text.x = element_blank()) +
	    coord_cartesian(ylim=c(0, 1))
	
	print(plot)
}