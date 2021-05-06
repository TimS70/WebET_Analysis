check_cat_distribution <- function(data) {
	
	# Enough data points for the categorical predictors? We need a sufficient 
	# ratio between the categories. Otherwise everything gets significant that 
	# happens in the larger category. 
	cat(paste(
	'Mean choseLL:', 
	mean(data$choseLL), '\n'))

	cat(paste(
		'LL_top vs. choseLL: \n',
		table(data$LL_top, data$choseLL)))
	
	temp = data %>% 
	    merge_by_subject(data_subject, 'age') %>%
	    merge_by_subject(data_subject, 'gender')
	
	temp$birthyear_bin = cut(
	                temp$age, 
	                breaks = c(0, 18, 30, 40, 50, 60, 70),
	                labels = c(   18, 30, 40, 50, 60, 70),
	                include.lowest=TRUE)
	
	print('Age vs. choseLL')
	print(table(temp$birthyear_bin, temp$choseLL))
	
	print('gender vs. choseLL: \n')
	print(table(temp$gender, temp$choseLL))
}