get_icc <- function(data, outcome) {
	icc_est <- ICCest(factor(data$run_id), 
		   data[, outcome], 
		   alpha=.05, 
		   CI.type="THD")
	
	print('ICC Estimation')
	print(icc_est)
}