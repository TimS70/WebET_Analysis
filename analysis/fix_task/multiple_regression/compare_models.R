library('MASS')

compare_models <- function(data, outcome) {

	data <- data %>%
		mutate(
			rt_c = scale(rt),
		    fps_c = scale(fps),
		    window_c = scale(window)
		)

	print('Testing control variables')
    lm_full_control <- lm(
		formula(
			paste(
				outcome,
				paste(
					'rt_c',
					'fps_c',
					'window_c',
					'ethnic',
					'vert_pos',
					'webcam_diag',
					sep=' + '
				),
			sep = ' ~ '
			)
		),
		data=data
	)

    print(step(lm_full_control))

	lm_control <- lm(formula(paste(
		outcome,
		'~ fps_c + window_c + ethnic + vert_pos + webcam_diag')),
		data=data
    )
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



grand_offset_model <- function(data) {

	outcome <- 'grand_offset'

	data <- data %>%
		mutate(
			rt_c = scale(rt),
		    fps_c = scale(fps),
		    window_c = scale(window),
			grand_offset = grand_offset * 100,
		)

	# print('Testing control variables')
    # lm_full_control <- lm(
	# 	formula(
	# 		paste(
	# 			outcome,
	# 			paste(
	# 				'rt_c',
	# 				'fps_c',
	# 				'window_c',
	# 				'ethnic',
	# 				'vert_pos',
	# 				'webcam_diag',
	# 				sep=' + '
	# 			),
	# 		sep = ' ~ '
	# 		)
	# 	),
	# 	data=data
	# )
	#
    # print(step(lm_full_control))

	control_variables <- 'rt_c'

	lm_control <- lm(formula(paste(
		outcome,
		'~',
		control_variables)),
		data=data
    )
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
