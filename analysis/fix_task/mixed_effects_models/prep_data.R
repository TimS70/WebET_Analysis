library(dplyr)

prep_trial_data <- function(data_subject, data_trial) {

    ## Intercept as Outcome	 
    grouped = data_subject %>%
    group_by(run_id) %>%
    dplyr::summarise(
        fps_subject = mean(fps),
        .groups = 'keep')
    
    data_trial = data_trial %>%
    merge_by_subject(data_subject, 'window') %>%
    merge_by_subject(data_subject, 'webcam_diag') %>%
    merge_by_subject(data_subject, 'vertPosition') %>%
    merge_by_subject(data_subject, 'ethnic') %>%
    mutate(y_pos_c = dplyr::recode(y_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
           x_pos_c = dplyr::recode(x_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
           x_pos_c_sq = dplyr::recode(x_pos, '0.2'=(1L), '0.5'=0L, '0.8'=1L),
           fps_c = scale(fps),
           window_c = scale(window),
           hit_mean = hit_mean * 100, 
           offset = offset * 100,
           grand_offset = grand_offset * 100,
           precision = precision * 100,
           offset_c = scale(offset), 
           trial = withinTaskIndex,
           precision_c = scale(precision),
           offset_log = log(offset),
           precision_log = log(precision)) %>%
    merge_by_subject(grouped, 'fps_subject') %>%
    mutate(fps_subject_c = fps - mean(grouped$fps_subject))
    
    return(data_trial)
}


prep_subject_data <- function(data_subject) {
  # Modify data
  data_subject <- data_subject %>%
    mutate(
      webcam_high_res = as.numeric(webcam_width >= 1280 & webcam_height >=720), 
      ethnic = factor(
        ethnic,
        levels = c("caucasian", "hispanic", "asian", "black"), # Faktorstufen
        labels = c("caucasian", "hispanic", "asian", "black")),
      webcam_diag = sqrt(webcam_width**2 + webcam_height**2),
      vertPosition = factor(vertPosition,
                            levels = c('a', 'b', 'c'),
                            labels = c('a', 'b', 'c')))
  
  return(data_subject)
}