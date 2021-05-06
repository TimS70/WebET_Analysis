compare_choice_models <- function(data, data_subject) {
	# https://stats.idre.ucla.edu/r/dae/mixed-effects-logistic-regression/
	glmer0_io = glmer(
	    choseLL ~ 1 + (1 | run_id), 
	    data = data,
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1)
	
	print('Intercept Only')
	print(summary(glmer0_io))
	
	# take pi^2 / 3 instead of the level-1 residual
	icc <- glmer0_io@theta[1]^2/ (glmer0_io@theta[1]^2 + (3.14159^2/3))
	
	print(paste(
		'ICC=', round(icc, 2), ': ',
		round(icc, 2)*100, 
		'%  of the variance are explained by between subject differences'))
	
	rand_std = as.data.frame(VarCorr(glmer0_io))$sdcor
	print(paste(
		'Mean log-odds for choice_LL vary across subjects. SD=',
		round(rand_std, 2), '.', 
		'Odds could increase by factor exp(rand_std)=',
		round(exp(rand_std), 2)))
	
	beta_0 = fixef(glmer0_io)[1][1]
	prob_intercept = exp(beta_0)/(1+exp(beta_0))
	
	print(paste(
		'Bias towards choseLL: Odds for LL choice is ', 
		'exp(beta_0) = ',
		round(exp(beta_0), 2), 
		'The average probability for choseLL is exp(beta_0)/(1+exp(beta_0)) = ',
		round(prob_intercept, 2)))
	
	# Random Intercept
	glmer1_ri = glmer(
	    choseLL ~ withinTaskIndex + rt_c + 
	    	optionIndex + attributeIndex + payneIndex + (1 | run_id), 
	    data = data,
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1)
	
	print('Random Intercept')
	print(summary(glmer1_ri))

	beta_0 = fixef(glmer1_ri)[1][1]
	coef_rt = fixef(glmer1_ri)[3]
	
	effect_rt = exp(beta_0 + coef_rt) / (1+(exp(beta_0+coef_rt)))
	cat(paste('Choice for LL decrease by factor', 
			  round(effect_rt, 2), 
			  'as rt increases by 1 SD in rt.'))
	
	glmer2_rirs = glmer(
	    choseLL ~ withinTaskIndex + rt_c + 
	    	optionIndex + attributeIndex + payneIndex  + 
	    	(optionIndex + attributeIndex + payneIndex  | run_id), 
	    data = data,
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1)
	
	print('Random Intercept - Random Slope')
	print(summary(glmer2_rirs))

	glmer2_rirs_2 = glmer(
	    choseLL ~ withinTaskIndex + rt_c + 
	    	optionIndex + attributeIndex + payneIndex  + 
	    	(attributeIndex  | run_id), 
	    data = data,
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1)
	
	print('Random Intercept - Random Slope 2')
	print(summary(glmer2_rirs_2))

	
	# Final Model
	glmer_final <- glmer2_ri

	# print(paste('glmer_wsc_io', summary(glmer_wsc_io), sep='\n'))
	# print(paste('glmer_wsc_ri', summary(glmer_wsc_ri), sep='\n'))
	# print(paste('glmer_wsc_rirs', summary(glmer_wsc_rirs), sep='\n'))
	
	print('Final Model:')
	print(summary(glmer_final))
	# confint(glmer_final, method="boot", n=50), 
				
	output_anova <- anova(glmer0_io, 
							glmer1_ri, 
							glmer2_rirs, 
							glmer2_rirs_2,
							glmer_final)
							# glmer_wsc_io,
							# glmer_wsc_ri,
							# glmer_wsc_rirs)
	print(output_anova)

	
	# Within Subject Centering

	grouped = data.frame(
	    data_subject$run_id,
	    data_subject$attributeIndex,
	    data_subject$optionIndex,
	    data_subject$payneIndex,
	    data_subject$choice_rt)

	names(grouped) = c('run_id',
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
	
	output_anova <- anova(glmer_wsc_io, 
						  glmer_wsc_ri,
						  glmer_wsc_rirs)
	print('Within-Subject-Centering Anova')
	print(output_anova)
	
	return(glmer_final)
	
}