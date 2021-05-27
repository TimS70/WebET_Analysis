compare_models <- function(data, outcome, control_variables, 
							exp_variables) {
	
	# 1) Emtpy model (intercept only)
	# ICC = 0.46. 46% of the variance can be explained by the variance between 
	# the subjects. Interdependence assumption of the simple linear regression 
	# is violated. We should to an MLA

	lmer0_io = lmer(formula(paste(outcome, '~ 1 + (1 | run_id)')), 
					data=data,
					REML=FALSE) # FML for comparing different fixed effects

	# 2) Intermediate models
	# Control variables
	# Control for the fact that the subjects start at different places 
	# regarding the accuracy of the eyetracking data. Standard error has 
	# increased. Subjects vary by about 0.12 (Jan 24) around the intercept. 
	# The RI model is way better than the IO model. Therefore, we should do 
	# an MLM.
	lmer1_control = lmer(
	    formula(paste0(outcome, ' ~  ', 
	    			   control_variables, 
	    			   ' + (1 | run_id)')), 
	    data=data,
	    REML=FALSE)
	
	# 3) Random Intercept
	lmer3_experimental = lmer(
	    formula(paste0(outcome, ' ~  ', 
	    			   control_variables, ' + ',
	    			   exp_variables, ' + ',
	    			   ' + (1 | run_id)')), 
	    data=data,
	    REML=FALSE)

	### Random slopes
	# Do not forget to look at the correlations among the random effects
	lmer4_rs = lmer(
	    formula(paste0(outcome, ' ~  ', 
	    			   control_variables, ' + ',
	    			   exp_variables, ' + ',
	    			   '(chin + glasses_binary | run_id)')), 
	    data=data,
	    REML=FALSE)
	
	## Intercept as Outcome	 
	lmer5_iao = lmer(
	    formula(paste0(outcome, ' ~  ', 
	    			   control_variables, ' + ',
	    			   exp_variables, ' + ',
	    			   'fps_subject_c + (1 | run_id)')), 
	    data=data,
	    REML=FALSE)
	summary(lmer5_iao)
	
	lmer6_iao_rs = lmer(
	    formula(paste0(outcome, ' ~  ', 
	    			   control_variables, ' + ',
	    			   exp_variables, ' + ',
	    			   'fps_subject_c + (chin + glasses_binary | run_id)')), 
	    data=data,
	    REML=FALSE)
	
	print(paste0(outcome, ': Intercept Only'))
	print(summary(lmer0_io)) 
	print(paste0(outcome, ': Control variables'))
	print(summary(lmer1_control)) 
	print(paste0(outcome, ': Experimental variables'))
	print(summary(lmer3_experimental)) 
	print(paste0(outcome, ': Random Slope'))
	print(summary(lmer4_rs)) 
	print(paste0(outcome, ': Intercept as Outcome'))
	print(summary(lmer5_iao)) 
	print(paste0(outcome, ': Intercept as Outcome plus Random Slope'))
	print(summary(lmer6_iao_rs)) 
	
	print('ANOVA Control')
	print(anova(lmer0_io, 
				lmer1_control, 
				lmer3_experimental,
				lmer4_rs))
	
	print('ANOVA RS')
	print(anova(lmer3_experimental, 
				lmer5_iao,
				lmer6_iao_rs))
	
	print('ANOVA RS vs. IAO RS')
	print(anova(lmer4_rs,
				lmer6_iao_rs))
	
	# confint(glmer_final, method="boot", n=50) # CI with Bootstrap
	# The confidence intervals should not include 1 to be significant
	
	if (outcome=='hit_mean') {
		print("lmer_final <- lmer6_iao_rs")
		lmer_final <- lmer6_iao_rs
	} else if (outcome=='offset') {
		print("lmer_final <- lmer6_iao_rs")
		lmer_final <- lmer6_iao_rs
	} else if (outcome=='precision') {
		print("lmer_final <- lmer6_iao_rs")
		lmer_final <- lmer6_iao_rs
	} else {
		print("lmer_final <- lmer6_iao_rs")
		lmer_final <- lmer0_io
	}
	
	return(lmer_final)
}


find_brm_models <- function(data, outcome) {
	
	## Intercept as Outcome	 
	grouped = data %>%
	    group_by(run_id) %>%
	    dplyr::summarise(
	    	fps_subject = mean(fps),
	    	.groups = 'keep')
	
	data = data %>%
		mutate(y_pos_c = recode(y_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
			   x_pos_c = recode(x_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
			   fps_c = scale(fps),
			   window_c = scale(window)) %>%
	    merge_by_subject(grouped, 'fps_subject') %>%
	    mutate(fps_subject_c = fps - mean(grouped$fps_subject))

	brm_0 = brm(formula(paste0(outcome, 
	    			   ' ~ withinTaskIndex + ',
	    			   'x_pos_c + y_pos_c + window_c + fps_c + ',
	    			   'glasses_binary + chin + ',
	    			   '(1 | run_id)')), 
		warmup = 1000, iter = 3000, 
		cores = 2, chains = 2, 
		data=data) 
	
	print(summary(brm_0))
	
	return(brm_0)
}
