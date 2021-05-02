offset_models <- function(data_trial) {
	
	data_trial = data_trial %>%
		mutate(y_pos_c = recode(y_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
			   x_pos_c = recode(x_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
			   fps_c = scale(fps),
			   window_c = scale(window))
	
	# 1) Emtpy model (intercept only)
	# ICC = 0.46. 46% of the variance can be explained by the variance between 
	# the subjects. Interdependence assumption of the simple linear regression 
	# is violated. We should to an MLA

	lmer0_io = lmer(offset ~ 1 + (1 | run_id), 
					data=data_trial,
					REML=FALSE) # FML for comparing different fixed effects
	
	icc_est <- ICCest(factor(data_trial$run_id), 
		   data_trial$offset, 
		   alpha=.05, 
		   CI.type="THD")
	
	print('ICC Estimation')
	print(icc_est)
	
	# 2) Intermediate models
	# Control variables
	# Control for the fact that the subjects start at different places 
	# regarding the accuracy of the eyetracking data. Standard error has 
	# increased. Subjects vary by about 0.12 (Jan 24) around the intercept. 
	# The RI model is way better than the IO model. Therefore, we should do 
	# an MLM.
		
	lmer1_control = lmer(
	    offset ~  withinTaskIndex + chinFirst + x_pos_c + y_pos_c + window_c + 
	    	fps_c + (1 | run_id), 
	    data=data_trial,
	    REML=FALSE)
	
	# 3) Random Intercept
	lmer3_experimental = lmer(
	    offset ~ withinTaskIndex + y_pos_c + glasses_binary + chin + 
	    	(1 | run_id), 
	    data=data_trial,
	    REML=FALSE)

	### Random slopes
	# Do not forget to look at the correlations among the random effects
	lmer4_rs = lmer(
	    offset ~ withinTaskIndex + y_pos_c + chin + glasses_binary + 
	    	(chin + glasses_binary | run_id), 
	    data=data_trial,
	    REML=FALSE)
	
	# Final Model
	lmer_final = lmer(
	    offset ~ withinTaskIndex + y_pos_c + chin + glasses_binary + 
	    	(chin + glasses_binary | run_id), 
	    data=data_trial,
	    REML=FALSE)
	
	print(summary(lmer0_io)) 
	print(summary(lmer1_control)) 
	print(summary(lmer3_experimental)) 
	print(summary(lmer4_rs)) 
	print(summary(lmer_final))
	
	print(anova(lmer0_io, 
				lmer1_control, 
				lmer3_experimental, 
				lmer4_rs, 
				lmer_final))
	
	# confint(glmer_final, method="boot", n=50) # CI with Bootstrap
	# The confidence intervals should not include 1 to be significant
	
	return(lmer_final)
}