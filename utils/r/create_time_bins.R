create_time_bins = function(data, n_bins) {
    data$time_bin = 0
    progress_bar <- progress_estimated(length(unique(data$run_id)), 0)
    
    for (subject in unique(data$run_id)){
        df_subject = data %>% filter(run_id == subject)
        
        for (trial in unique(df_subject$withinTaskIndex)) {
            df_trial = df_subject %>% filter(withinTaskIndex == trial)
            
            this_time_bin = cut(
                df_trial$t_task, n_bins,
                labels = c(1:n_bins),
                include.lowest=TRUE)
            
            data = data %>%
                mutate(time_bin=replace(
                    time_bin, 
                    run_id==subject & withinTaskIndex==trial, 
                    this_time_bin))
        }
        progress_bar$pause(0.1)$tick()$print()
    }
    return(data)
}