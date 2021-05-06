simple_slopes <- function(data, model, upper=TRUE) {
		# SD
	sd_ai = sd(data$attributeIndex, na.rm = TRUE)
	
	if (upper) {
		data$ai_sd = data$attributeIndex + sd_ai
	} else {
		data$ai_sd = data$attributeIndex - sd_ai
	}
	
	glmer_sd = glmer(
	    choseLL ~ withinTaskIndex + rt_c + ai_sd + (1 | run_id), 
	    data = data, 
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"))

	print('Simple Slopes Upper')
	print(summary(glmer_sd))
	
	return(glmer_sd)
}
