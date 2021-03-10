summarize_datasets = function(data_et, data_trial, data_subject) {
    et_trials = data_et %>%
    dplyr::select(run_id, trial_index) %>%
    distinct()

    summary = data.frame(
        name = c(
            'data_et',
            'data_trial',
            'data_subject'
        ),
        runs = c( 
            length(unique(data_et$run_id)),
            length(unique(data_trial$run_id)),
            length(unique(data_subject$run_id))
        ),
        n_trials = c(
            nrow(data_trial),
            nrow(et_trials), 
            '-'
        )
    ) 
    
    print(summary)
}