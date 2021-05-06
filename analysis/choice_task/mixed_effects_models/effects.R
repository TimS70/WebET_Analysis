source(file.path(path_analysis, 'simple_slopes.R'))
 # - No effects but better model fit
 # - No Pseudo R² because it is a logistic ME regression model

 # - The effect of "payneIndex_cmc" is not significant, payneIndex_cmc OR = 0.83, 
 # 95% CI [0.67, 1] (has to be beyond 1 to be significant). Imagine it to be 
 # signficant: with an increase of the Payne Index of 1 (e.g. if they switch 
 # from neutral to only within option transitions), results in 0.67 times the 
 # chance (a lower chance) of choosing the delayed reward. 
 # - Same for the ones with low (-1 SD) and high (+1 SD) Payne Index (If you 
 # have random slope, compare the different levels. 

odds_ratio <- function(model, data) {
	OR <- exp(fixef(model))
	CI <- exp(confint(model, parm="beta_")) # it can be slow (~ a few minutes). As alternative, the much faster but less precise Wald's method can be used: CI <- exp(confint(FM,parm="beta_",method="Wald")) 
	
	model_ul <- simple_slopes(data=data, model=model, upper=TRUE)
	model_ll <- simple_slopes(data=data, model=model, upper=FALSE)

	
	or_sd_1 <- exp(fixef(model_ul))
	ci_sd_1 <- exp(confint(model_ul, parm="beta_")) 
	
	or_sd_2 <- exp(fixef(model_ll))
	ci_sd_2 <- exp(confint(model_ll, parm="beta_")) 
	
	OR_CI<-rbind(
	    cbind(OR,CI), 
	    cbind(or_sd_1, ci_sd_1)[3,], 
	    cbind(or_sd_2, ci_sd_2)[3,])
	
	rownames(OR_CI) = c(
	    rownames(cbind(OR,CI)), 
	    "attributeIndex_cmc_sd1", 
	    "attributeIndex_cmc_sd2")
	
	print(paste('Odds Ratio: ', OR_CI, sep='\n'))
}
