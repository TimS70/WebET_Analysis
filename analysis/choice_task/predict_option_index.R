predict_option_index <- function(data) {
	lme_ll_top = lmer(
	    optionIndex ~ LL_top + (1 | run_id), 
	    data = data,
	    REML = FALSE)
	
	print(summary(lme_ll_top))
	print(confint(lme_ll_top, method="boot", n=50))
}