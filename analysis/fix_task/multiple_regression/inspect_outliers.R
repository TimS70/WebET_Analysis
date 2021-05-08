source(file.path(path_analysis, 'compare_models.R'))
source(file.path(path_analysis, 'predict_validation.R'))

inspect_outliers <- function(data_subject, data_et) {
	
	# Exclude no outliers
	# data_subject <- data_subject %>% 
	# 	filter(!run_id %in% data_subject[c(166, 179, 192), 'run_id'])
	
	output <- data_subject %>% 
		filter(offset > 0.4) %>%
		dplyr::select(run_id, glasses_binary, hit_mean, offset, precision) %>%
		arrange(offset)
	
	print(output)
	
	output <- data_et %>% 
		filter(run_id == 379) %>%
		group_by(x_pos, y_pos) %>% 
		dplyr::summarise(n = n(), 
						 x_m = mean(x), 
						 y_m = mean(y))

	print(output)
	
	# compare_models(data=data_subject %>% filter(offset<0.5), 
	# 			   outcome='offset')
	# runs_left <- data_test %>%
	# 	group_by(glasses_binary) %>%
	# 	dplyr::summarise(n = n(), 
	# 					 .groups = 'keep')
	# 
	# print('runs left')
	
	
	# Scatter plots showed some runs without any variation in gaze points	
	runs_cal_error_no_glasses <- c(268, 325, 243)
	runs_cal_error_glasses <- c(425, 488)
	runs_cal_error <- c(runs_cal_error_glasses, runs_cal_error_no_glasses)

	compare_models(data=data_subject %>% filter(!run_id %in% runs_cal_error), 
				   outcome='offset')
	
	predict_validation(data=data_subject %>% 
					   	filter(!run_id %in% runs_cal_error))
	
}