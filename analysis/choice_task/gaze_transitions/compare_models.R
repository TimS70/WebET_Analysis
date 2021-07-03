compare_models <- function(data, get_ci=FALSE) {

	data <- data %>% mutate(
		rt_c = scale(trial_duration_exact)
	)

	glmer_1 <- glmer(
    choseLL ~ withinTaskIndex + rt_c +
		optionIndex +
		attributeIndex +
    	payneIndex +
		(1 | run_id),
    data = data, 
    family = binomial, 
    control = glmerControl(optimizer = "bobyqa"),
    nAGQ = 1)

	glmer_2 <- glmer(
	    choseLL ~ withinTaskIndex + rt_c +
			optionIndex +
			attributeIndex +
	    	payneIndex  +
			cluster2 +
	    	(1 | run_id), 
	    data = data, 
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1)
	
	glmer_3 <- glmer(
	    choseLL ~ withinTaskIndex + rt_c +
			optionIndex +
			attributeIndex +
	    	payneIndex +
			cluster3 +
	    	(1 | run_id), 
	    data = data, 
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1)
	
	glmer_4 <- glmer(
	    choseLL ~ withinTaskIndex + rt_c +
			optionIndex +
			attributeIndex +
	    	payneIndex +
			cluster4 +
	    	(1 | run_id), 
	    data = data, 
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1)
	
	fixef(glmer_2)[5]
	fixef(glmer_3)[5]
	fixef(glmer_4)[5]
	
	# confint(m_cluster_2, method="boot", n=50) # Bootstrap
	anova_output <- anova(
		glmer_1,
		glmer_2,
		glmer_3,
		glmer_4)
	
	print(anova_output)

	glmer_final <- glmer_2

	if (get_ci) {
		print(confint(glmer_final, method="boot", n=500))
	}

	return(glmer_final)
}