test_assumptions <- function(model, data) {
	
	# print('Test assumptions for')
	# print(formula(model))
	
	path <- file.path('results', 'plots', 'choice_task', 'assumptions')
	dir.create(path, showWarnings = FALSE)

	# HLM diag overview
	# case_delete() #iteratively delete groups corresponding to the levels of
	# a hierarchical linear model, using lmer to fit the models for each deleted 
	# case

	#covratio() #calculate measures of the change in the covariance matrices 
	# for the fixed effects based on the deletion of an observation, or group 
	# of observations,
	
	#diagnostics() #is used to compute deletion diagnostics for a hierarchical 
	# linear model based on the building blocks returned by case_delete.
	
	#HLMresid() #extracts residuals from a hierarchical linear model fit 
	# using lmer. Can provide a variety of different types of residuals based 
	# upon the specifications when you call the function
	
	#leverage() #calculates the leverage of a hierarchical linear model fit
	
	#mdffits() #calculate measures of the change in the fixed effects 
	# estimates based on the deletetion of an observation, or group of 
	# observations
	
	
	
	
	# Linarity, Normality of the residuals, over- and under-dispersion
	par(mar = rep(2, 4))
	simulation_output = simulateResiduals(model, plot=F, use.u = T)
	png(file = file.path(path, 'dharma.png'),
		width = 800, height = 400)
	my_plot <- plot(simulation_output)
	print(my_plot)
	dev.off()

	# Test for over- and underdispersion
	my_result <- testDispersion(simulation_output)
	print(my_result)

	# For continuous predictors
	my_result <- testQuantiles(simulation_output)
	print(my_result)

	for (pred in c('run_id')) {
		print(paste('Check residuals for predictor', pred))
		png(file = file.path(path, paste0('residuals_', pred, '.png')),
			width = 400, height = 400)
		
		my_plot <- plotResiduals(simulation_output,
								 form = data %>% dplyr::pull(!!as.symbol(pred)),
								 xlab=pred)
		dev.off()
	}
	
	# Linearity
	## Linear relationship between predicted log(choseLL) and the predictors
	# http://www.sthda.com/english/articles/36-classification-methods-essentials/148-logistic-regression-assumptions-and-diagnostics-in-r/
	predictors = c('attributeIndex', 'optionIndex', 'payneIndex')
	
	data_plot = data %>%
		mutate(predict_choseLL_prob = 
	        predict(model, type = "response"),
	        logit = log(predict_choseLL_prob/(1-predict_choseLL_prob))) %>%
	    dplyr::select(c(logit, predictors)) %>%
	    gather(key = "predictors", value = "predictor_value", -logit)
	
	ggplot(data_plot, aes(logit, predictor_value)) +
	    geom_point(size = 0.5, alpha = 0.5) +
	    geom_smooth(method = "loess") + 
	    theme_bw() + 
	    facet_wrap(~predictors, scales = "free_y")
	ggsave(file.path(path, 'linearity.png'), width=7, height=4)
	
	# Multicollinearity
	# compute variance inflation factor. " As a rule of thumb, a VIF value 
	# that exceeds 5 or 10 indicates a problematic amount of collinearity"
	print(car::vif(model))
}