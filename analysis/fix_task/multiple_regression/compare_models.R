compare_models <- function(data, outcome) {
	
	data <- data %>%
		mutate(rt_c = scale(rt),
			   fps_c = scale(fps),
			   window_c = scale(window))
	
	lm_control <- lm(formula(paste(outcome, 
								   '~ fps_c + window_c + ethnic + vert_pos + webcam_diag')),
					 data=data) 
	print('lm_control')
	print(summary(lm_control))

	lm_experiment <- update(lm_control, . ~ . + glasses_binary)
	print('lm_experiment')
	print(summary(lm_experiment))
	
	output_anova <- anova(lm_control, lm_experiment)
	print('ANOVA')
	print(output_anova)
	
	return(lm_experiment)
}


hit_ratio_models <- function(data, outcome='hit_ratio') {
		
	data = data %>%
		mutate(fps_c = scale(fps),
			   window_c = scale(window), 
			   offset_c = scale(offset), 
			   precision_c = scale(precision))
	
	lm_control <- lm(formula(paste(outcome, '~ fps_c + window_c + ethnic + vert_pos + webcam_diag')),
					 data=data) 
	print('lm_control')
	print(summary(lm_control))
	
	lm_experiment <- update(lm_control, . ~ . + glasses_binary)
	print('lm_experiment')
	print(summary(lm_experiment))
	
	lm_off_prec <- update(lm_experiment, . ~ . + offset_c + precision_c)
	print('lm_off_prec')
	print(summary(lm_off_prec))
	
	output_anova <- anova(lm_control, lm_experiment, lm_off_prec)
	print('ANOVA')
	print(output_anova)
	
	return(lm_experiment)
}
