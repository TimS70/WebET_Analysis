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
	
	# box_cox(data=data, model=model, outcome='offset')

}


box_cox <- function(model, data, outcome) {
	
	path=file.path(path_results, 'assumptions', paste(outcome, 'box', sep='_'))
	dir.create(path, showWarnings = FALSE)
	
	model_box <- np.boxcoxmix(formula(model),
							  groups = data_trial$run_id, data = data_trial,
							  K = 3, tol = 1, start = "gq", lambda=-1, 
							  verbose=FALSE)
	
	plot(model_box)
	
	dir.create(path, showWarnings = FALSE)
	data$residuals = residuals(model_box, type='pearson')
	ggplot(data, aes(x=residuals, y=!!as.symbol(outcome))) + 
		geom_point() + 
		ggtitle(paste('Distribution Standardized Residuals against', outcome)) + 
		xlab('Predicted') + 
		ylab('Standardized Residuals') +
		theme_bw()
		
	ggsave(filename = file.path(path, 'linearity.png'), width = 4, height = 4)
	
	
	# Heteroscedasticity
	data = data %>%
	    mutate(res = residuals(model_box),
	    	   res_sq = (abs(res)^2))
	
	levene_model <- lm(res_sq ~ run_id, data=data)
	print('Testing for Heteroscedasticity')
	print(anova(levene_model))
	
	png(file = file.path(path, 'res_prob.png'), width = 400, height = 400)
	# https://cran.r-project.org/web/packages/boxcoxmix/boxcoxmix.pdf
	print(plot(model_box, plot.opt=3))
	dev.off()

	png(file = file.path(path, 'res_hist.png'), width = 400, height = 400)
	# https://cran.r-project.org/web/packages/boxcoxmix/boxcoxmix.pdf
	print(plot(model_box, plot.opt=6))
	dev.off()	
}