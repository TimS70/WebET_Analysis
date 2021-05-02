library(robustlmm)

offset_robust <- function(data) {
	# Robust LMM
	lmer_offset_r = rlmer(
	    offset_100 ~ withinTaskIndex + x_pos_c + y_pos_c + fps + chin + glasses_binary 
	    + (chin | run_id),
	    	#(chin + glasses_binary | run_id), 
	    data=data)

	print(summary(lmer_offset_r)) # look at the robustness weights
	print(confint(lmer_offset_r, method="boot", n=50))

	my_plot <- plot(lmer_offset) # qq-plot
	print(my_plot)	
}