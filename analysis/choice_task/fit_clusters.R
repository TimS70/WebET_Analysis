fit_clusters = function(data_trial) {
	m_cluster_1 = glmer(
    choseLL ~ withinTaskIndex + rt_c + attributeIndex + 
    	payneIndex + (1 | run_id), 
    data = data_trial, 
    family = binomial, 
    control = glmerControl(optimizer = "bobyqa"),
    nAGQ = 1)

	m_cluster_2 = glmer(
	    choseLL ~ withinTaskIndex + rt_c + attributeIndex + 
	    	payneIndex  + cluster2 + 
	    	(1 | run_id), 
	    data = data_trial, 
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1)
	
	m_cluster_3 = glmer(
	    choseLL ~ withinTaskIndex + rt_c + attributeIndex + 
	    	payneIndex + cluster3 + 
	    	(1 | run_id), 
	    data = data_trial, 
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1)
	
	m_cluster_4 = glmer(
	    choseLL ~ withinTaskIndex + rt_c + attributeIndex + 
	    	payneIndex + cluster4 + 
	    	(1 | run_id), 
	    data = data_trial, 
	    family = binomial, 
	    control = glmerControl(optimizer = "bobyqa"),
	    nAGQ = 1)
	
	fixef(m_cluster_2)[5]
	fixef(m_cluster_3)[5]
	fixef(m_cluster_4)[5]
	
	# confint(m_cluster_2, method="boot", n=50) # Bootstrap
	anova(m_cluster_1, m_cluster_2, m_cluster_3, m_cluster_4)
}