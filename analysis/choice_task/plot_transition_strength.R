plot_transition_strength = function(data, cluster=1, 
									parralel_distance=0.01, 
									cluster_name='cluster2') {

	grouped = data %>% 
		dplyr::select(!!as.symbol(cluster_name),
					  trans_type_0,   
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
		dplyr::summarise(across(everything(), list(mean))) %>%
		t()
	
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
					 size = round(grouped['trans_type_aLLtLL_1', cluster], 2),
					 arrow = arrow(length = unit(0.4, "cm"))) +
		
		geom_segment(aes(xend = 0.4, 
						 yend = 0.25 + 2*parralel_distance,
						 x = 0.6, 
						 y = 0.25 + 2*parralel_distance), 
					 size = round(grouped['trans_type_tLLaLL_1', cluster], 2),
					 arrow = arrow(length = unit(0.4, "cm"))) +
		
		geom_segment(aes(x = 0.4, 
						 y = 0.75 - 2*parralel_distance, 
						 xend = 0.6, 
						 yend = 0.75 - 2*parralel_distance), 
				 size = round(grouped['trans_type_aSStSS_1', cluster], 2),
				 arrow = arrow(length = unit(0.4, "cm"))) +
		
		geom_segment(aes(xend = 0.4, 
						 yend = 0.75 + 2*parralel_distance, 
						 x = 0.6, 
						 y = 0.75 + 2*parralel_distance), 
				 size = round(grouped['trans_type_tSSaSS_1', cluster], 2),
				 arrow = arrow(length = unit(0.4, "cm"))) +
		
		geom_segment(aes(x = 0.4 + parralel_distance, 
						 y = 0.4 - parralel_distance, 
						 xend = 0.6 + parralel_distance, 
						 yend = 0.6 - parralel_distance), 
				 size = round(grouped['trans_type_aLLtSS_1', cluster], 2),
				 arrow = arrow(length = unit(0.4, "cm"))) +
		
		geom_segment(aes(xend = 0.4 - parralel_distance, 
						 yend = 0.4 + parralel_distance, 
						 x = 0.6 - parralel_distance, 
						 y = 0.6 + parralel_distance), 
				 size = round(grouped['trans_type_tSSaLL_1', cluster], 2),
				 arrow = arrow(length = unit(0.4, "cm"))) +
	
		geom_segment(aes(x = (0.05 + 0.9 * 0.2) - parralel_distance, 
						 y = 0.4, 
						 xend = (0.05 + 0.9 * 0.2) - parralel_distance, 
						 yend = 0.6), 
				 size = round(grouped['trans_type_aLLaSS_1', cluster], 2),
				 arrow = arrow(length = unit(0.4, "cm"))) +
		
		geom_segment(aes(xend = (0.05 + 0.9 * 0.2) + parralel_distance, 
						 yend = 0.4, 
						 x = (0.05 + 0.9 * 0.2) + parralel_distance, 
						 y = 0.6), 
				 size = round(grouped['trans_type_aSSaLL_1', cluster], 2),
				 arrow = arrow(length = unit(0.4, "cm"))) +
		
		geom_segment(aes(x = (0.05 + 0.9 * 0.8) - parralel_distance, 
						 y = 0.4, 
						 xend = (0.05 + 0.9 * 0.8) - parralel_distance, 
						 yend = 0.6), 
				 size = round(grouped['trans_type_tLLtSS_1', cluster], 2),
				 arrow = arrow(length = unit(0.4, "cm"))) +
		
		geom_segment(aes(xend = (0.05 + 0.9 * 0.8) + parralel_distance, 
						 yend = 0.4, 
						 x = (0.05 + 0.9 * 0.8) + parralel_distance, 
						 y = 0.6), 
				 size = round(grouped['trans_type_tSStLL_1', cluster], 2),
				 arrow = arrow(length = unit(0.4, "cm"))) +
	
		
		geom_segment(aes(x = 0.6 - parralel_distance, 
						 y = 0.4 - parralel_distance, 
						 xend = 0.4 - parralel_distance, 
						 yend = 0.6 - parralel_distance), 
				 size = round(grouped['trans_type_tLLaSS_1', cluster], 2),
				 arrow = arrow(length = unit(0.4, "cm"))) +
		
		geom_segment(aes(xend = 0.6 + parralel_distance, 
						 yend = 0.4 + parralel_distance, 
						 x = 0.4 + parralel_distance, 
						 y = 0.6 + parralel_distance), 
				 size = round(grouped['trans_type_aSStLL_1', cluster], 2),
				 arrow = arrow(length = unit(0.4, "cm"))) +
		
		xlim(0, 1) + ylim(1, 0) +
		theme_bw()
	
	print(my_plot)
}