source(file.path(root, 'analysis', 'fix_task', 'assumptions.R'))

transform_model <- function(data, model, outcome) {
	
	outcome_log <- paste(outcome, 'log', sep='_')
	outcome_sqrt <- paste(outcome, 'sqrt', sep='_')
	
	data[, outcome_log] = log(data[, outcome])
	data[, outcome_sqrt] = sqrt(data[, outcome])

	print('Transform models: ')

	lmer_basic <- lmer(formula(model), data=data, REML=FALSE)

	if (outcome != 'hit_mean') { 
		lmer_log <- update(lmer_basic, log(.) ~ .)
		test_assumptions(model=lmer_log, data=data, outcome=outcome_log)
	}
	
	lmer_sqrt <- update(lmer_basic, sqrt(.) ~ .)
	test_assumptions(model=lmer_sqrt, data=data, outcome=outcome_sqrt)
	
	
	# Box Cox
	# model_box <- np.boxcoxmix(
	# 	offset ~ withinTaskIndex + y_pos_c + chin + glasses_binary + 
	# 		(chin + glasses_binary | run_id), 
	# 	groups = data_trial$run_id, data = data_trial,
	# 					   K = 3, tol = 1, start = "gq", lambda=1, verbose=FALSE)
	# 
	# plot(model_box)
	

	
}
