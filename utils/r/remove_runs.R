remove_runs = function(data) {
	print('Remove missing et indices:')
    print(deparse(substitute(data)))
    print(paste('length raw: ', nrow(data)))
    data = data %>%
        filter(!(run_id %in% exclude_runs))
    print(paste('length cleaned: ', nrow(data)))
    return(data)
}