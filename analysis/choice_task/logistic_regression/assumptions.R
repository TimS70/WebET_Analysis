test_assumptions <- function(model, data, path) {
	dir.create(path, showWarnings = F)
	linearity(model=model, data=data, path)
	influential_points(model=model, path=path)
	mutlicollinearity(model=model)
}

linearity <- function(model, data, path) {
	predictors = c('attributeIndex', 'optionIndex_2', 'payneIndex')
	
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
}

influential_points <- function(model, path) {
	png(file = file.path(path, 'influence.png'), width = 800, height = 400)
	my_plot <- plot(model, which = 4, id.n = 3)
	dev.off()
}

mutlicollinearity <- function(model) {
	print(car::vif(model))
}