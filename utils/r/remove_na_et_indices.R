remove_na_et_indices = function(data_raw) {

    data = data_raw %>% filter(
            !is.na(attributeIndex) &
            !is.na(optionIndex) &
            !is.na(payneIndex))
    
    print(deparse(substitute(data_raw)))
    print(paste('Raw: ', nrow(data_raw)))
    print(paste('Cleaned: ', nrow(data)))


    return(data)
}