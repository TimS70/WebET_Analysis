data=data_subject
path=file.path(path_results, 'glasses')

examine_glasses <- function(data, path) {

	for (var in c('hit_mean', 'offset')) {
		my_plot <- ggplot(data=data, aes(x=factor(glasses_binary), 
										 y=!!as.symbol(var))) +
		    geom_violin(fill="gray", size=0.5) +
		    stat_summary(fun=mean,geom="point",shape=45,size=10, color="white") +
		    theme_bw()+ylim(0,1.03)+xlab("") + 
		    ylab(var) +
		    xlab("Glasses") + 
		    theme(text=element_text(size=15))
		print(my_plot)
		ggsave(file.path(path, paste0('glasses_vs_', var, '.png')), 
			   width=5.5, height=5)
	}
	
	output <- data %>% 
		group_by(glasses_binary) %>%
		dplyr::summarise(
			hit_mean_m = mean(hit_mean),
			hit_mean_sd = sd(hit_mean),
			offset_m = mean(offset), 
			offset_sd = sd(offset),
			precision_m = mean(precision),
			precision_sd = sd(precision)) %>%
		t() %>%
		round(3)
	print(output*100)
	sd(data_subject$offset)
	
	png(file = file.path(path, paste0('hit_mean_vs_glasses.png')))
	plot(hit_mean ~ factor(glasses_binary), data=data_subject)
	dev.off()
	
	png(file = file.path(path, paste0('offset_vs_glasses.png')))
	plot(offset ~ factor(glasses_binary), data=data_subject)
	dev.off()
	
	for (i in 0:1) {
		my_plot <- ggplot(
			data_subject %>% filter(glasses_binary == i), 
			aes(x=offset, y=hit_mean)) +
			geom_point(size=2, shape=1) +
			xlim(0, 1) + ylim(0, 1) +
			ggtitle(paste('hit_mean vs. offset for glasses =', i))
		png(file = file.path(path,
							 paste0('offset_vs_hit_mean_glasses_', i, '.png')))
		print(my_plot)
		dev.off()
	}

	# Systematic Offset
	ggplot(data=data_subject, aes(x=factor(glasses_binary), y=grand_offset)) +
		geom_boxplot(outlier.colour="black", outlier.shape=16,
					 outlier.size=2, notch=FALSE) + 
		ggtitle('Glasses vs. systematic offset')
	
	t.test(grand_offset ~ glasses_binary,
		   data=data_subject %>% filter(!is.na(glasses_binary)))
	
	this_run <- unique(data_et$run_id)[1]
	ggplot(data=data_et %>% 
		   	filter(run_id==this_run) %>%
			slice(0:500),
		   aes(x, y)) +
		geom_point() + 
		ggtitle(paste0('Scatter plot, run_id=', this_run))
		
}
