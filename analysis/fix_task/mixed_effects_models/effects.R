pseudo_r2_l1 <- function(data_trial, outcome) {
	# Use formulas without random slopes (Snijders & Bosker, 2012)
	m0 <- lmer(paste(outcome, '(1 | run_id)', sep = '~'),
           data=data_trial,
           REML=FALSE)
	m1 <- lmer(paste(outcome, 'withinTaskIndex + (1 | run_id)', sep = '~'),
	           data=data_trial,
	           REML=FALSE)
	
	L1_m0 <- sigma(m0)^2 # L1-Residualvarianz RIO Modell
	L1_m1 <- sigma(m1)^2 # L1-Residualvarianz RI Modell
	
	pseudo_r2 <- (L1_m0 - L1_m1)/L1_m0

	print(paste0('Reduction of L1 variance due to chin: ', 
				 round(100 * pseudo_r2, 2), '%'))
	
	return(pseudo_r2)
	
	
}

pseudo_r2_l2 <- function(data_trial, outcome) {
	# Use formulas without random slopes (Snijders & Bosker, 2012)
	m0 <- lmer(paste(outcome, '(1 | run_id)', sep = '~'),
           data=data_trial,
           REML=FALSE)
	m1 <- lmer(paste(outcome, 'withinTaskIndex + (1 | run_id)', sep = '~'),
	           data=data_trial,
	           REML=FALSE)

	L2_m0 <- unlist(summary(m0)$var) # Interceptvarianz RI Modell
	L2_m1 <- unlist(summary(m1)$var) # Interceptvarianz IAO Modell
	
	pseudo_r2 <- (L2_m0 - L2_m1)/L2_m0
	
	print(paste0('Reduction of L2 variance due to chin: ', 
				 round(100 * pseudo_r2, 2), '%'))
	
	return(pseudo_r2)
}