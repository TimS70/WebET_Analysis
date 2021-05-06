test_clusters <- function(model, data) {

	m_cluster_2 = update(model, . ~ . + cluster2)
	m_cluster_3 = update(model, . ~ . + cluster3)
	m_cluster_4 = update(model, . ~ . + cluster4)
	
	# fixef(m_cluster_2)[5]
	# fixef(m_cluster_3)[5]
	# fixef(m_cluster_4)[5]
	
	# confint(m_cluster_2, method="boot", n=50) # Bootstrap
	output_anova <- anova(model, m_cluster_2, m_cluster_3, m_cluster_4)
	print(output_anova)
}