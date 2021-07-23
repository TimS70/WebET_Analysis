library("brms")
library("lmerTest")

pseudo_r <- function(data, control_variables, outcome) {
    
    lmer1_control <- lmer(
        formula(paste0(
            outcome,
            ' ~ ',
            control_variables,
            ' + (1 | run_id)'
        )),
        data=data,
        REML=FALSE
    )
    
    lmer2_chin <- lmer(
        formula(paste0(
            outcome,
            ' ~ ',
            control_variables,
            ' + chin ',
            ' + (1 | run_id)'
        )),
        data=data,
        REML=FALSE
    )
    
    # Snijders & Bosker (2012): Do not use random slopes models
    pseudor <- (sigma(lmer1_control)^2-sigma(lmer2_chin)^2)/sigma(lmer1_control)^2
    print(paste0('The chin rest effect reduces the unexplained variance for the outcome ',
                 outcome, ' on level 1 by ', round(pseudor*100, 2), '%.'))
    
    lmer3_glasses <- lmer(
        formula(paste0(
            outcome,
            ' ~ ',
            control_variables,
            ' + chin + glasses_binary',
            ' + (1 | run_id)'
        )),
        data=data,
        REML=FALSE
    )
    
    
    pseudor <- (unlist(summary(lmer2_chin)$var)-unlist(summary(lmer3_glasses)$var))/unlist(summary(lmer2_chin)$var)
    print(
        paste0('Glasses reduce the unexplained variance of the intercept of the outcome ', outcome, 
               ', compared to the model that only contains the control variables and chin-rest, by ', round(pseudor*100, 2), '%.')
    )
}

hit_ratio_models <- function(data, apa_path=FALSE, get_ci=TRUE) {
  
    # print('Testing control variables')
    # lmer_full_control <- lmer(
    #     hit_mean ~
    #     trial +
    #     chinFirst +
    #     x_pos_c +
    #     y_pos_c +
    #     fps_c +
    #     window_c +
    #     webcam_diag +
    #     vertPosition +
    #     ethnic +
    #     fps_subject_c +
    #     (1 | run_id),
    #     data=data)
    #
    # print(step(lmer_full_control))
    
    control_variables <- 'trial + x_pos_c_sq + fps_c + fps_subject_c'
  
  # 1) Emtpy model (intercept only)
  # ICC = 0.46. 46% of the variance can be explained by the variance between 
  # the subjects. Interdependence assumption of the simple linear regression 
  # is violated. We should to an MLA
  
    lmer_0_io <- lmer(
        hit_mean ~ 1 + (1 | run_id), 
        data=data,
        REML=FALSE
    ) # FML for comparing different fixed effects
  
    # 2) Intermediate models
    # Control variables
    # Control for the fact that the subjects start at different places 
    # regarding the accuracy of the eyetracking data. Standard error has 
    # increased. Subjects vary by about 0.12 (Jan 24) around the intercept. 
    # The RI model is way better than the IO model. Therefore, we should do 
    # an MLM.
    lmer_1_control <- lmer(
        formula(paste0(
            'hit_mean ~ ',
            control_variables,
            ' + (1 | run_id)'
        )),
        data=data,
        REML=FALSE
    )
  
  # 3) Random Intercept
    lmer_2_exp <- lmer(
        formula(paste0(
            'hit_mean ~ ',
            control_variables,
            ' + chin + glasses_binary + (1 | run_id)'
        )),
        data=data,
        REML=FALSE
    )  
  ### Random slopes
  # Do not forget to look at the correlations among the random effects
    lmer_3_rs <- lmer(
        formula(paste0(
            'hit_mean ~ ',
            control_variables,
            ' + chin + glasses_binary', 
            ' + (chin | run_id)'
        )),
        data=data,
        REML=FALSE
    ) 
  
    print(summary(lmer_0_io)) 
    print(summary(lmer_1_control))

    if (get_ci) {
        ci <- confint(lmer_1_control, method="boot", n=500, oldNames=FALSE) # CI with Bootstrap
        print(ci)
    }

    print(summary(lmer_2_exp))

    if (get_ci) {
        ci <- confint(lmer_2_exp, method="boot", n=500, oldNames=FALSE) # CI with Bootstrap
        print(ci)
    }

    print(summary(lmer_3_rs)) 

    if (get_ci) {
        ci <- confint(lmer_3_rs, method="boot", n=500, oldNames=FALSE) # CI with Bootstrap
        print(ci)
    }

    print('ANOVA Control')
    print(anova(
        lmer_0_io,
        lmer_1_control,
        lmer_2_exp,
        lmer_3_rs)
    )
    
    pseudo_r(
        data=data, 
        control_variables=control_variables, 
        outcome='hit_mean'
    )

    lmer_final <- lmer_3_rs
    print('lmer_final <- lmer_3_rs')

    return(lmer_final)
}


offset_models <- function(data, apa_path=FALSE, get_ci=TRUE, output_model='best') {

    # print('Testing control variables')
    #
    # lmer_full_control <- lmer(
    #     offset ~
    #     trial +
    #     chinFirst +
    #     x_pos_c +
    #     y_pos_c +
    #     window_c +
    #     fps_c +
    #     webcam_diag +
    #     vertPosition +
    #     ethnic +
    #     fps_subject_c +
    #     (1 | run_id),
    #     data=data)
    #
    # print(lmerTest::step(object=lmer_full_control))
    
    control_variables <- 'trial + x_pos_c_sq + y_pos_c + fps_c + fps_subject_c'
    
    # 1) Emtpy model (intercept only)
    # ICC = 0.46. 46% of the variance can be explained by the variance between 
    # the subjects. Interdependence assumption of the simple linear regression 
    # is violated. We should to an MLA
    
    lmer_0_io = lmer(
        offset ~ 1 + (1 | run_id), 
        data=data,
        REML=FALSE
    ) # FML for comparing different fixed effects
    
    # 2) Intermediate models
    # Control variables
    # Control for the fact that the subjects start at different places 
    # regarding the accuracy of the eyetracking data. Standard error has 
    # increased. Subjects vary by about 0.12 (Jan 24) around the intercept. 
    # The RI model is way better than the IO model. Therefore, we should do 
    # an MLM.
    lmer_1_control = lmer(
        formula(paste0(
            'offset ~ ',
            control_variables,
            ' + (1 | run_id)'
        )),
        data=data,
        REML=FALSE
    )
    
    # 3) Random Intercept
    lmer_2_exp <- lmer(
        formula(paste0(
            'offset ~ ',
            control_variables,
            ' + chin + glasses_binary + (1 | run_id)'
        )),
        data=data,
        REML=FALSE
    )  
    ### Random slopes
    # Do not forget to look at the correlations among the random effects
    lmer_3_rs <- lmer(
        formula(paste0(
            'offset ~ ',
            control_variables,
            ' + chin + glasses_binary', 
            ' + (chin | run_id)'
        )),
        data=data,
        REML=FALSE
    ) 
    
    print(summary(lmer_0_io)) 
    print(summary(lmer_1_control))

    if (get_ci) {
        ci <- confint(lmer_1_control, method="boot", n=500, oldNames=FALSE) # CI with Bootstrap
        print(ci)
    }

    print(summary(lmer_2_exp))

    if (get_ci) {
        ci <- confint(lmer_2_exp, method="boot", n=500, oldNames=FALSE) # CI with Bootstrap
        print(ci)
    }

    print(summary(lmer_3_rs)) 

    if (get_ci) {
        ci <- confint(lmer_3_rs, method="boot", n=500, oldNames=FALSE) # CI with Bootstrap
        print(ci)
    }

    
    pseudo_r(
        data=data, 
        control_variables=control_variables, 
        outcome='offset'
    )
    
    print('ANOVA Control')
    print(anova(
        lmer_0_io,
        lmer_1_control,
        lmer_2_exp,
        lmer_3_rs))

    if (output_model=='random_intercept') {
        lmer_final <- lmer_2_exp
        print('lmer_final <- lmer_2_exp')
    }

    if (output_model=='best') {
        lmer_final <- lmer_3_rs
        print('lmer_final <- lmer_3_rs')
    }

    return(lmer_final)
}


grand_offset_models <- function(data, apa_path=FALSE, get_ci=TRUE) {

    # print('Testing control variables')
    #
    # lmer_full_control <- lmer(
    #     offset ~
    #     trial +
    #     chinFirst +
    #     x_pos_c +
    #     y_pos_c +
    #     window_c +
    #     fps_c +
    #     webcam_diag +
    #     vertPosition +
    #     ethnic +
    #     fps_subject_c +
    #     (1 | run_id),
    #     data=data)
    #
    # print(lmerTest::step(object=lmer_full_control))

    control_variables <- 'trial + x_pos_c_sq + y_pos_c + fps_c + fps_subject_c'

    # 1) Emtpy model (intercept only)
    # ICC = 0.46. 46% of the variance can be explained by the variance between
    # the subjects. Interdependence assumption of the simple linear regression
    # is violated. We should to an MLA

    lmer_0_io = lmer(
        grand_offset ~ 1 + (1 | run_id),
        data=data,
        REML=FALSE
    ) # FML for comparing different fixed effects

    # 2) Intermediate models
    # Control variables
    # Control for the fact that the subjects start at different places
    # regarding the accuracy of the eyetracking data. Standard error has
    # increased. Subjects vary by about 0.12 (Jan 24) around the intercept.
    # The RI model is way better than the IO model. Therefore, we should do
    # an MLM.
    lmer_1_control = lmer(
        formula(paste0(
            'grand_offset ~ ',
            control_variables,
            ' + (1 | run_id)'
        )),
        data=data,
        REML=FALSE
    )

    # 3) Random Intercept
    lmer_2_exp <- lmer(
        formula(paste0(
            'grand_offset ~ ',
            control_variables,
            ' + chin + glasses_binary + (1 | run_id)'
        )),
        data=data,
        REML=FALSE
    )
    ### Random slopes
    # Do not forget to look at the correlations among the random effects
    lmer_3_rs <- lmer(
        formula(paste0(
            'grand_offset ~ ',
            control_variables,
            ' + chin + glasses_binary',
            ' + (chin | run_id)'
        )),
        data=data,
        REML=FALSE
    )

    print(summary(lmer_0_io))
    print(summary(lmer_1_control))

    if (get_ci) {
        ci <- confint(lmer_1_control, method="boot", n=500, oldNames=FALSE) # CI with Bootstrap
        print(ci)
    }

    print(summary(lmer_2_exp))

    if (get_ci) {
        ci <- confint(lmer_2_exp, method="boot", n=500, oldNames=FALSE) # CI with Bootstrap
        print(ci)
    }

    print(summary(lmer_3_rs))

    if (get_ci) {
        ci <- confint(lmer_3_rs, method="boot", n=500, oldNames=FALSE) # CI with Bootstrap
        print(ci)
    }

    print('ANOVA Control')
    print(anova(
        lmer_0_io,
        lmer_1_control,
        lmer_2_exp,
        lmer_3_rs))

    lmer_final <- lmer_3_rs
    print('lmer_final <- lmer_3_rs')

    return(lmer_final)
}


precision_models <- function(data, apa_path=FALSE, get_ci=TRUE) {
    
    # print('Testing control variables')
    #
    # lmer_full_control <- lmer(precision ~
    #                               trial +
    #                               chinFirst +
    #                               x_pos_c +
    #                               y_pos_c +
    #                               window_c +
    #                               fps_c +
    #                               webcam_diag +
    #                               vertPosition +
    #                               ethnic +
    #                               fps_subject_c +
    #                               (1 | run_id),
    #                           data=data)
    #
    # print(step(lmer_full_control))
    
    control_variables <- 'trial + y_pos_c + fps_c + fps_subject_c'
    
    # 1) Emtpy model (intercept only)
    # ICC = 0.46. 46% of the variance can be explained by the variance between 
    # the subjects. Interdependence assumption of the simple linear regression 
    # is violated. We should to an MLA
    
    lmer_0_io <- lmer(
        precision ~ 1 + (1 | run_id), 
        data=data,
        REML=FALSE
    ) # FML for comparing different fixed effects
    
    # 2) Intermediate models
    # Control variables
    # Control for the fact that the subjects start at different places 
    # regarding the accuracy of the eyetracking data. Standard error has 
    # increased. Subjects vary by about 0.12 (Jan 24) around the intercept. 
    # The RI model is way better than the IO model. Therefore, we should do 
    # an MLM.
    lmer_1_control <- lmer(
        formula(paste0(
            'precision ~ ',
            control_variables,
            ' + (1 | run_id)'
        )),
        data=data,
        REML=FALSE
    )
    
    # 3) Random Intercept
    lmer_2_exp <- lmer(
        formula(paste0(
            'precision ~ ',
            control_variables,
            ' + chin + glasses_binary + (1 | run_id)'
        )),
        data=data,
        REML=FALSE
    )  
    ### Random slopes
    # Do not forget to look at the correlations among the random effects
    lmer_3_rs <- lmer(
        formula(paste0(
            'precision ~ ',
            control_variables,
            ' + chin + glasses_binary', 
            ' + (chin | run_id)'
        )),
        data=data,
        REML=FALSE
    ) 
    
    print(summary(lmer_0_io)) 
    print(summary(lmer_1_control))

    if (get_ci) {
        ci <- confint(lmer_1_control, method="boot", n=500) # CI with Bootstrap
        print(ci)
    }

    print(summary(lmer_2_exp)) 
    if (get_ci) {
        ci <- confint(lmer_2_exp, method="boot", n=500) # CI with Bootstrap
        print(ci)
    }

    print(summary(lmer_3_rs))

    if (get_ci) {
        ci <- confint(lmer_3_rs, method="boot", n=500) # CI with Bootstrap
        print(ci)
    }

    
    pseudo_r(
        data=data, 
        control_variables=control_variables, 
        outcome='precision'
    )
    
    print('ANOVA')
    print(anova(
        lmer_0_io,
        lmer_1_control,
        lmer_2_exp,
        lmer_3_rs)
    )

    print('ANOVA')
    print(anova(lmer_1_control, 
                lmer_3_rs))    

    lmer_final <- lmer_3_rs
    print('lmer_final <- lmer_3_rs')

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
