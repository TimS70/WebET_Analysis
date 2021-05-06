compare_models <- function(data) {

# 	 - See Sommet, 2017
#  - choseLL is more likely than choseSS. 
#  - Logisitic regression does not have residuals because it predicts probabilities not concrete values.
#  - Predict log-odds (exp(beta)). Odds increase by the factor exp(beta), when the predictor changes in one unit. beta=0 means odds=1. 
#  - A positive Attribute Index indicates more fixations on the amount attributes
#  - A negative Option Index indicates more fixations on the delayed option
#  - A negative Payne Index indicates more transitions within attributes 
	
	print('Test logistic model: ')
	m_null = glm(choseLL ~ 1,
         data = data_subject %>%
		 	filter(!is.na(attributeIndex) & !is.na(payneIndex) &
		 		   !is.na(optionIndex)), 
         family = binomial(link = "logit"))
	print('Null model:')
	print(summary(m_null))
	
	m1 = glm(choseLL ~ 1 + choice_rt + 
			 	I(optionIndex^2) + attributeIndex + payneIndex,
	         data = data_subject %>%
			 	filter(!is.na(optionIndex) & 
			 		   !is.na(attributeIndex) &
			 		   !is.na(payneIndex)), 
	         family = binomial(link = "logit"))

	print('Full model:')
	print(summary(m1))
	output_anova <- anova(m_null, m1)
	print('ANOVA')
	print(output_anova)
	
	return(m1)
}