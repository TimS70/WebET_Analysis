plot_transition_strength = function(data, cluster=1, 
									parralel_distance=0.01, 
									cluster_name='cluster2', 
									strength_factor=0.25,
									undirected=FALSE, 
									cutoff=0,
									title='Transition clusters') {

	n_transitions = data_trial %>% 
		dplyr::select(trans_type_aLLtLL,
					  trans_type_tLLaLL,        
	  				  trans_type_tLLaSS,
					  trans_type_aSStLL, 
	  				  trans_type_aLLaSS,
					  trans_type_aSSaLL,        
	 				  trans_type_aSStSS,
					  trans_type_tSSaSS, 
					  trans_type_tLLtSS,
					  trans_type_tSStLL,         
					  trans_type_aLLtSS,
					  trans_type_tSSaLL) %>%
		sum()

	if (undirected) {
		# data$trans_type_aLLtLL = data$trans_type_aLLtLL + data$trans_type_tLLaLL        
		# data$trans_type_tLLaSS = data$trans_type_tLLaSS + data$trans_type_aSStLL 
		# data$trans_type_aLLaSS = data$trans_type_aLLaSS + data$trans_type_aSSaLL        
		# data$trans_type_aSStSS = data$trans_type_aSStSS + data$trans_type_tSSaSS 
		# data$trans_type_tLLtSS = data$trans_type_tLLtSS + data$trans_type_tSStLL         
		# data$trans_type_aLLtSS = data$trans_type_aLLtSS + data$trans_type_tSSaLL	
		
		grouped = data %>% 
			dplyr::select(!!as.symbol(cluster_name),
							trans_type_aLLtLL,
							trans_type_tLLaSS,
							trans_type_aLLaSS,
							trans_type_aSStSS,
							trans_type_tLLtSS,
							trans_type_aLLtSS) %>%
			dplyr::group_by(!!as.symbol(cluster_name)) %>%
			dplyr::summarise(
				n = n(),
				aLLtLL = mean(trans_type_aLLtLL),        
				tLLaSS = mean(trans_type_tLLaSS), 
				aLLaSS = mean(trans_type_aLLaSS),        
				aSStSS = mean(trans_type_aSStSS), 
				tLLtSS = mean(trans_type_tLLtSS),         
				aLLtSS = mean(trans_type_aLLtSS)) %>%
				t()
		
		grouped[grouped < cutoff] = 0
		
		my_plot = ggplot() +
			geom_text(aes(x= (0.05 + 0.9 * 0.2), y= 0.25, 
						  label='[amount LL]')) +
			geom_text(aes(x= (0.05 + 0.9 * 0.8), y= 0.25, 
						  label='[time LL]')) +
			geom_text(aes(x= (0.05 + 0.9 * 0.2), y= 0.75, 
						  label='[amount SS]')) +
			geom_text(aes(x= (0.05 + 0.9 * 0.8), y= 0.75, 
						  label='[time SS]')) +

			geom_segment(aes(x = 0.4, 
							 y = 0.25, 
							 xend = 0.6, 
							 yend = 0.25), 
						 size = round(
						 	grouped['aLLtLL', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +
			geom_segment(aes(x = 0.4, 
							 y = 0.75, 
							 xend = 0.6, 
							 yend = 0.75), 
					 size = round(
					 	grouped['aSStSS', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +
			
			geom_segment(aes(x = 0.4, 
							 y = 0.4, 
							 xend = 0.6, 
							 yend = 0.6), 
					 size = round(
					 	grouped['aLLtSS', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +					 			 
		
			geom_segment(aes(x = (0.05 + 0.9 * 0.2), 
							 y = 0.4, 
							 xend = (0.05 + 0.9 * 0.2), 
							 yend = 0.6), 
					 size = round(
					 	grouped['aLLaSS', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +					 			 
			
			geom_segment(aes(x = (0.05 + 0.9 * 0.8), 
							 y = 0.4, 
							 xend = (0.05 + 0.9 * 0.8), 
							 yend = 0.6), 
					 size = round(
					 	grouped['tLLtSS', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +					 			 
			
			geom_segment(aes(x = 0.6, 
							 y = 0.4, 
							 xend = 0.4, 
							 yend = 0.6), 
					 size = round(
					 	grouped['tLLaSS', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +					 			 

			# Reverse Arrows
			geom_segment(aes(xend = 0.4, 
							 yend = 0.25, 
							 x = 0.6, 
							 y = 0.25), 
						 size = round(
						 	grouped['aLLtLL', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +
			geom_segment(aes(xend = 0.4, 
							 yend = 0.75, 
							 x = 0.6, 
							 y = 0.75), 
					 size = round(
					 	grouped['aSStSS', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +
			
			geom_segment(aes(xend = 0.4, 
							 yend = 0.4, 
							 x = 0.6, 
							 y = 0.6), 
					 size = round(
					 	grouped['aLLtSS', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +					 			 
		
			geom_segment(aes(xend = (0.05 + 0.9 * 0.2), 
							 yend = 0.4, 
							 x = (0.05 + 0.9 * 0.2), 
							 y = 0.6), 
					 size = round(
					 	grouped['aLLaSS', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +					 			 
			
			geom_segment(aes(xend = (0.05 + 0.9 * 0.8), 
							 yend = 0.4, 
							 x = (0.05 + 0.9 * 0.8), 
							 y = 0.6), 
					 size = round(
					 	grouped['tLLtSS', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +					 			 
			
			geom_segment(aes(xend = 0.6, 
							 yend = 0.4, 
							 x = 0.4, 
							 y = 0.6), 
					 size = round(
					 	grouped['tLLaSS', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +	
			
			xlim(0, 1) + ylim(1, 0) +
			theme_bw() +
			theme(text=element_text(size=15),
				  plot.title = element_text(size = 20, face = "bold")) + 
			ggtitle(title) +
			xlab('x-Position [% screen size]') +
			ylab('y-Position [% screen size]') 
	} else {
		grouped = data %>% 
			dplyr::select(!!as.symbol(cluster_name),
						  trans_type_aLLtLL,
						  trans_type_tLLaLL,        
		  				  trans_type_tLLaSS,
						  trans_type_aSStLL, 
		  				  trans_type_aLLaSS,
						  trans_type_aSSaLL,        
		 				  trans_type_aSStSS,
						  trans_type_tSSaSS, 
						  trans_type_tLLtSS,
						  trans_type_tSStLL,         
						  trans_type_aLLtSS,
						  trans_type_tSSaLL) %>%
			dplyr::group_by(!!as.symbol(cluster_name)) %>%
			dplyr::summarise(
				n = n(),
				aLLtLL = mean(trans_type_aLLtLL),
				tLLaLL = mean(trans_type_tLLaLL),        
				tLLaSS = mean(trans_type_tLLaSS),
				aSStLL = mean(trans_type_aSStLL), 
				aLLaSS = mean(trans_type_aLLaSS),
				aSSaLL = mean(trans_type_aSSaLL),        
				aSStSS = mean(trans_type_aSStSS),
				tSSaSS = mean(trans_type_tSSaSS), 
				tLLtSS = mean(trans_type_tLLtSS),
				tSStLL = mean(trans_type_tSStLL),         
				aLLtSS = mean(trans_type_aLLtSS),
				tSSaLL = mean(trans_type_tSSaLL)) %>%
				t()
		
		grouped[grouped < cutoff] = 0 
		
		my_plot = ggplot() +
			geom_text(aes(x= (0.05 + 0.9 * 0.2), y= 0.25, 
						  label='[amount LL]')) +
			geom_text(aes(x= (0.05 + 0.9 * 0.8), y= 0.25, 
						  label='[time LL]')) +
			geom_text(aes(x= (0.05 + 0.9 * 0.2), y= 0.75, 
						  label='[amount SS]')) +
			geom_text(aes(x= (0.05 + 0.9 * 0.8), y= 0.75, 
						  label='[time SS]')) +
			
			geom_segment(aes(x = 0.4, 
							 y = 0.25 - 2*parralel_distance, 
							 xend = 0.6, 
							 yend = 0.25 - 2*parralel_distance), 
						 size = round(grouped['aLLtLL', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +
			
			geom_segment(aes(xend = 0.4, 
							 yend = 0.25 + 2*parralel_distance,
							 x = 0.6, 
							 y = 0.25 + 2*parralel_distance), 
						 size = round(grouped['tLLaLL', cluster] * strength_factor, 2),
						 arrow = arrow(length = unit(0.5, "cm"))) +
			
			geom_segment(aes(x = 0.4, 
							 y = 0.75 - 2*parralel_distance, 
							 xend = 0.6, 
							 yend = 0.75 - 2*parralel_distance), 
					 size = round(grouped['aSStSS', cluster] * strength_factor, 2),
					 arrow = arrow(length = unit(0.5, "cm"))) +
			
			geom_segment(aes(xend = 0.4, 
							 yend = 0.75 + 2*parralel_distance, 
							 x = 0.6, 
							 y = 0.75 + 2*parralel_distance), 
					 size = round(grouped['tSSaSS', cluster] * strength_factor, 2),
					 arrow = arrow(length = unit(0.5, "cm"))) +
			
			geom_segment(aes(x = 0.4 + parralel_distance, 
							 y = 0.4 - parralel_distance, 
							 xend = 0.6 + parralel_distance, 
							 yend = 0.6 - parralel_distance), 
					 size = round(grouped['aLLtSS', cluster] * strength_factor, 2),
					 arrow = arrow(length = unit(0.5, "cm"))) +
			
			geom_segment(aes(xend = 0.4 - parralel_distance, 
							 yend = 0.4 + parralel_distance, 
							 x = 0.6 - parralel_distance, 
							 y = 0.6 + parralel_distance), 
					 size = round(grouped['tSSaLL', cluster] * strength_factor, 2),
					 arrow = arrow(length = unit(0.5, "cm"))) +
		
			geom_segment(aes(x = (0.05 + 0.9 * 0.2) - parralel_distance, 
							 y = 0.4, 
							 xend = (0.05 + 0.9 * 0.2) - parralel_distance, 
							 yend = 0.6), 
					 size = round(grouped['aLLaSS', cluster] * strength_factor, 2),
					 arrow = arrow(length = unit(0.5, "cm"))) +
			
			geom_segment(aes(xend = (0.05 + 0.9 * 0.2) + parralel_distance, 
							 yend = 0.4, 
							 x = (0.05 + 0.9 * 0.2) + parralel_distance, 
							 y = 0.6), 
					 size = round(grouped['aSSaLL', cluster] * strength_factor, 2),
					 arrow = arrow(length = unit(0.5, "cm"))) +
			
			geom_segment(aes(x = (0.05 + 0.9 * 0.8) - parralel_distance, 
							 y = 0.4, 
							 xend = (0.05 + 0.9 * 0.8) - parralel_distance, 
							 yend = 0.6), 
					 size = round(grouped['tLLtSS', cluster] * strength_factor, 2),
					 arrow = arrow(length = unit(0.5, "cm"))) +
			
			geom_segment(aes(xend = (0.05 + 0.9 * 0.8) + parralel_distance, 
							 yend = 0.4, 
							 x = (0.05 + 0.9 * 0.8) + parralel_distance, 
							 y = 0.6), 
					 size = round(grouped['tSStLL', cluster] * strength_factor, 2),
					 arrow = arrow(length = unit(0.5, "cm"))) +
		
			
			geom_segment(aes(x = 0.6 - parralel_distance, 
							 y = 0.4 - parralel_distance, 
							 xend = 0.4 - parralel_distance, 
							 yend = 0.6 - parralel_distance), 
					 size = round(grouped['tLLaSS', cluster] * strength_factor, 2),
					 arrow = arrow(length = unit(0.5, "cm"))) +
			
			geom_segment(aes(xend = 0.6 + parralel_distance, 
							 yend = 0.4 + parralel_distance, 
							 x = 0.4 + parralel_distance, 
							 y = 0.6 + parralel_distance), 
					 size = round(grouped['aSStLL', cluster] * strength_factor, 2),
					 arrow = arrow(length = unit(0.5, "cm"))) +
			
			xlim(0, 1) + ylim(1, 0) +
			theme_bw() + 
			theme(text=element_text(size=15),
				  plot.title = element_text(size = 20, face = "bold")) + 
			ggtitle(title) +
			xlab('x-Position [% screen size]') +
			ylab('y-Position [% screen size]') 
	}
	
	
	print(row.names(grouped))
	
	print(round(grouped, 2))
	print(paste('N Transitions :', n_transitions))
	print(my_plot)
}