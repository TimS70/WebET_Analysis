library(lmerTest)
library(cAIC4)

source(file.path(root, 'utils', 'r', 'merge_by_subject.R'))


logistic_effect <- function(model, beta_index, beta_name) {
    beta_0 <- fixef(model)[1][1]
    beta_x <- fixef(model)[beta_index]
    my_effect <- exp(beta_0 + beta_x) / (1+(exp(beta_0+beta_x)))
    cat(paste('Choice for LL decrease by factor', 
              round(my_effect, 2), 
              'as', 
              beta_name,
              'increases by 1.'))
    return(my_effect)
}


compare_choice_models <- function(data, data_subject, get_ci=FALSE) {
    
    # data <- data %>%
    #     merge_by_subject(data_subject, 'gender') %>%
    #     merge_by_subject(data_subject, 'degree') %>%
    #     merge_by_subject(data_subject, 'age') %>%
    #     merge_by_subject(data_subject, 'ethnic') %>%
    #     mutate(
    #         ethnic = factor(
    #             ethnic,
    #             levels = c("caucasian", "hispanic", "asian", "black"), # Faktorstufen
    #             labels = c("caucasian", "hispanic", "asian", "black")
    #         )
    #     )
    # 
    # glmer_full <- glmer(
    #     choseLL ~ withinTaskIndex + rt_c + 
    #         gender +  
    #         degree + 
    #         age + 
    #         chinFirst + 
    #         ethnic + 
    #         LL_top + 
    #         (1 | run_id),
    #     data=data
    # )
    # 
    # stepcAIC(glmer_full)
    
	# https://stats.idre.ucla.edu/r/dae/mixed-effects-logistic-regression/
	glmer_0_io = glmer(
	    choseLL ~ 1 + (1 | run_id), 
	    data = data,
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1
	)
	
	# Control variables
	glmer_1_control = glmer(
	    choseLL ~ withinTaskIndex + rt_c + (1 | run_id), 
	    data = data,
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1
    )

	# Random Intercept
	glmer_2_ri = glmer(
	    choseLL ~ withinTaskIndex + rt_c + 
	    	optionIndex + attributeIndex + payneIndex + (1 | run_id), 
	    data = data,
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1
    )

	glmer_3_rs = glmer(
	    choseLL ~ withinTaskIndex + rt_c + 
	    	optionIndex + attributeIndex + payneIndex  + 
	    	(optionIndex + attributeIndex + payneIndex  | run_id), 
	    data = data,
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1
    )
	
	print('Control variables')	
	print(summary(glmer_1_control))

	if (get_ci) {
		ci <- confint(glmer_1_control, method="boot", n=500) # CI with Bootstrap
		print(ci)
	}

	print('Experimental variables')
	print(summary(glmer_2_ri))

	if (get_ci) {
		ci <- confint(glmer_2_ri, method="boot", n=500) # CI with Bootstrap
		print(ci)
	}

	print('Random Intercept - Random Slope')
	print(summary(glmer_3_rs))

	if (get_ci) {
		ci <- confint(glmer_3_rs, method="boot", n=500) # CI with Bootstrap
		print(ci)
	}
	
    logistic_effect(
        model=glmer_3_rs,
        beta_index=3,
        beta_name='rt'
    )
	
	print('Intercept Only')
	print(summary(glmer_0_io))
	
	# take pi^2 / 3 instead of the level-1 residual
	icc <- glmer_0_io@theta[1]^2/ (glmer_0_io@theta[1]^2 + (3.14159^2/3))
	
	print(paste(
	    'ICC=', round(icc, 2), ': ',
	    round(icc, 2)*100, 
	    '%  of the variance are explained by between subject differences'))
	
	rand_std = as.data.frame(VarCorr(glmer_0_io))$sdcor
	print(paste(
	    'Mean log-odds for choice_LL vary across subjects. SD=',
	    round(rand_std, 2), '.', 
	    'Odds could increase by factor exp(rand_std)=',
	    round(exp(rand_std), 2)))
	
	beta_0 = fixef(glmer_0_io)[1][1]
	prob_intercept = exp(beta_0)/(1+exp(beta_0))
	
	print(paste(
	    'Bias towards choseLL: Odds for LL choice is ', 
	    'exp(beta_0) = ',
	    round(exp(beta_0), 2), 
	    'The average probability for choseLL is exp(beta_0)/(1+exp(beta_0)) = ',
	    round(prob_intercept, 2)))
	
    logistic_effect(
        model=glmer_3_rs,
        beta_index=2,
        beta_name='trial'
    )
	
	output_anova <- anova(
        glmer_0_io, 
        glmer_1_control,
        glmer_2_ri,
        glmer_3_rs)

	print(output_anova)

	# Final Model
	glmer_final <- glmer_2_ri
	print('lmer_final <- glmer_2_ri')
	
	return(glmer_final)
}


within_subject_models <- function() {
    # Within Subject Centering
    
    grouped = data.frame(
        data_subject$run_id,
        data_subject$attributeIndex,
        data_subject$optionIndex,
        data_subject$payneIndex,
        data_subject$choice_rt)
    
    names(grouped) = c(
        'run_id',
        'cluster_mean_AI',
        'cluster_mean_OI',
        'cluster_mean_PI',
        'cluster_mean_rt')
    
    for (col in names(grouped)[2:5]){
        if (col %in% names(data)) {
            data = data %>% dplyr::select(!col)
        }
    }
    
    data = merge(data, grouped, by='run_id')
    
    data$attributeIndex_cmc = data$attributeIndex -
        data$cluster_mean_AI
    
    data$optionIndex_cmc = data$optionIndex -
        data$cluster_mean_OI
    
    data$payneIndex_cmc = data$payneIndex -
        data$cluster_mean_PI
    
    glmer_wsc_io = glmer(
        choseLL ~ 1 + withinTaskIndex + rt_c + (1 | run_id),
        data = data %>% filter(!is.na(attributeIndex_cmc) &
                                   !is.na(payneIndex_cmc) &
                                   !is.na(optionIndex_cmc)),
        family = binomial,
        control = glmerControl(optimizer = "bobyqa"),
        nAGQ = 1)
    
    print('WSC: Intercept Only')
    print(summary(glmer_wsc_io))
    
    glmer_wsc_ri = glmer(
        choseLL ~ withinTaskIndex + rt_c +
            optionIndex_cmc + attributeIndex_cmc + payneIndex_cmc +
            (1 | run_id),
        data = data %>% filter(!is.na(attributeIndex_cmc) &
                                   !is.na(payneIndex_cmc) &
                                   !is.na(optionIndex_cmc)),
        family = binomial,
        control = glmerControl(optimizer = "bobyqa"),
        nAGQ = 1)
    
    print('WSC: Random Intercept')
    print(summary(glmer_wsc_ri))
    
    glmer_wsc_rirs = glmer(
        choseLL ~  withinTaskIndex + rt_c +
            optionIndex_cmc + attributeIndex_cmc + payneIndex_cmc +
            (optionIndex_cmc + attributeIndex_cmc + payneIndex_cmc | run_id),
        data = data %>% filter(!is.na(attributeIndex_cmc) &
                                   !is.na(payneIndex_cmc) &
                                   !is.na(optionIndex_cmc)),
        family = binomial,
        control = glmerControl(optimizer = "bobyqa"),
        nAGQ = 1)
    
    print('WSC: Random Intercept - Random Slope')
    print(summary(glmer_wsc_rirs))
    
    output_anova <- anova(
        glmer_wsc_io,
        glmer_wsc_ri,
        glmer_wsc_rirs)
    
    print('Within-Subject-Centering Anova')
    print(output_anova)
}