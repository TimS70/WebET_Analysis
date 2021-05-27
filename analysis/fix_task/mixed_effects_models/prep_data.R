prep_data <- function(data_subject, data_trial) {

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
    mutate(y_pos_c = recode(y_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
           x_pos_c = recode(x_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
           fps_c = scale(fps),
           window_c = scale(window),
           offset_c = scale(offset), 
           precision_c = scale(precision),
           offset_log = log(offset),
           precision_log = log(precision)) %>%
    merge_by_subject(grouped, 'fps_subject') %>%
    mutate(fps_subject_c = fps - mean(grouped$fps_subject))
  
    return(data_trial)
}