plot_et_time_bins = function(data_time_bins) {

	runs_not_enough_bins = data_time_bins %>%
	    group_by(run_id, choseTop) %>%
	    dplyr::summarise(
	    	n=length(unique(time_bin)),
	    	.groups = 'keep') %>%
	    filter(n<5) %>%
	    dplyr::pull(run_id)
	
	print('These runs have less than 5 time bins: ')
	print(runs_not_enough_bins)

	# t-test
	for (bin in unique(data_time_bins$time_bin)) {
	    print(t.test(p_lookTop ~ choseTop,
	                 data=data_time_bins %>%
	                     filter(time_bin==bin &
	                            !(run_id %in% runs_not_enough_bins)),
	                 paired=TRUE))
		
		print(cohen.d(p_lookTop ~ choseTop, pooled=TRUE, paired=TRUE, 
					  data=data_time_bins %>%
	                     filter(time_bin==bin &
	                            !(run_id %in% runs_not_enough_bins))))
	}

	
	bin_plot = ggplot(data_time_bins, 
		aes(x=factor(time_bin), y=p_lookTop, 
			fill=factor(choseTop, c('1', '0')))) + 
	geom_violin(alpha=.7, size=0, position="dodge") +
	stat_summary(
		fun=mean, geom="point", 
		shape=45, size=10, position=position_dodge(.9), 
		aes(color=factor(choseTop, c('1', '0')))) +
	scale_colour_manual( 
		values=c("1"="black", "0"="white"), name="", 
		labels=c("Chose top", "Chose bottom")) +
	scale_fill_grey(
		start=.3, end=.7, name="",
	  	labels=c("Chose top", "Chose bottom")) +
	xlab("Time bins") + ylab("Proportion looking top") +
	ylim(0, 1) + 
	theme_bw() + 
	theme(text=element_text(size=20), legend.position="bottom")
	
	# Violin Plot
	# bin_plot = ggplot(data_time_bins, 
	#        aes(x=factor(time_bin), y=p_lookTop, fill=choseTop)) +
	#     geom_split_violin(alpha=0.7, size=1, position="dodge") +
	#     stat_summary(
	#         fun=mean, geom="point",
	#         shape=45,size=10,
	#         position=position_dodge(.9), 
	#         aes(color=factor(choseTop, c('1', '0')))) +
	#     theme_bw() + 
	#     theme(text=element_text(size=20), 
	#     legend.position="bottom") +
	#     ggtitle('Eye-tracking time bins') +
	#     scale_colour_manual(
	#         values=c("1"="black", "0"="white"), 
	#         name="", 
	#         labels=c("Chose Top", "Chose Bottom")) +
	#     scale_fill_grey(
	#         start=.3, end=.7, name="",
	#         labels=c("Chose Top", "Chose Bottom")) +
	#     ylab("Proportion looking top") +
	#     xlab("Time bins")
	
	print(bin_plot)
}