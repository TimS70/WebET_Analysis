library(DHARMa)
	
test_assumptions <- function(model, data, outcome) {
	
	dir.create(file.path('results', 'plots', 'fix_task', 'assumptions'),
			   showWarnings = FALSE)

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
	simulation_output = simulateResiduals(model, plot=T, use.u = T)
	print(simulation_output)
	my_plot <- plot(simulation_output)
	print(my_plot)

	# Test for over- and underdispersion
	my_result <- testDispersion(simulation_output)
	print(my_result)

	# For continuous predictors
	my_result <- testQuantiles(simulation_output)
	print(my_result)

	for (pred in c('run_id')) {
		print(paste('Check residuals for predictor', pred))
		my_plot <- plotResiduals(simulation_output,
								 form = data %>% dplyr::pull(!!as.symbol(pred)),
								 xlab=pred)
		print(my_plot)
	}
	
	# Classical Residual plots, without DHARMa

	# Standardized residuals
	data$residuals = residuals(model, type='pearson')
	ggplot(data, aes(x=residuals, y=!!as.symbol(outcome))) + 
		geom_point() + 
		ggtitle(paste('Distribution Standardized Residuals against', outcome)) + 
		xlab('Predicted') + 
		ylab('Standardized Residuals') +
		theme_bw()
		
	ggsave(filename = file.path(path_results, 'assumptions', 
								paste(outcome, 'linearity.png', sep='_')))
	
	# Heteroscedasticity
	data = data %>%
	    mutate(res = residuals(model),
	    	   res_sq = (abs(res)^2))
	
	levene_model <- lm(res_sq ~ run_id, data=data)
	print('Testing for Heteroscedasticity')
	print(anova(levene_model))
	
	jpeg(file = file.path(path_results, 'assumptions', 
						  paste(outcome, 'heteroscedasticity.jpeg', sep='_')))
	plot(model)
	dev.off()
	
	# Normal distribution of residuals
	my_plot <- qqmath(model, id=0.05)
	print(my_plot)
	
	# Multicollinearity
	car::vif(model)
	
}