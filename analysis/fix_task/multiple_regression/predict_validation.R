predict_validation <- function(data) {

	data <- data %>%
		mutate(hit_suffice = as.numeric(hit_ratio > 0.8),
			   fps_c = scale(fps),
			   window_c = scale(window))
	
	model <- glm(
		hit_suffice ~ 1 + glasses_binary + fps_c + window_c + 
			ethnic + vert_pos,
		data = data,
		family = binomial(link = "logit"))
	output_model <- summary(model)
	print(output_model)
}