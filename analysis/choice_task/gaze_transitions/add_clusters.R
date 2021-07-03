library('stats')

add_clusters <- function(data, n_cluster=2) {
    
    # data <- data %>% mutate(
    #     trans_type_aLLtLL = trans_type_aLLtLL + trans_type_tLLaLL,
    #     trans_type_tLLaSS = trans_type_tLLaSS + trans_type_aSStLL,
    #     trans_type_aLLaSS = trans_type_aLLaSS + trans_type_aSSaLL,
    #     trans_type_aSStSS = trans_type_aSStSS + trans_type_tSSaSS,
    #     trans_type_tLLtSS = trans_type_tLLtSS + trans_type_tSStLL,
    #     trans_type_aLLtSS = trans_type_aLLtSS + trans_type_tSSaLL
    # )

    data <- data %>% mutate(
        trans_type_aLLtLL = scale(trans_type_aLLtLL),
        trans_type_tLLaSS = scale(trans_type_tLLaSS),
        trans_type_aLLaSS = scale(trans_type_aLLaSS),
        trans_type_aSStSS = scale(trans_type_aSStSS),
        trans_type_tLLtSS = scale(trans_type_tLLtSS),
        trans_type_aLLtSS = scale(trans_type_aLLtSS)
    )

    km.res <- kmeans(
         x=data[, c(
                'trans_type_aLLtLL',
                'trans_type_tLLaSS',
                'trans_type_aLLaSS',
                'trans_type_aSStSS',
                'trans_type_tLLtSS',
                'trans_type_aLLtSS'
            )
         ],
         centers=n_cluster,
         iter.max = 10,
         nstart = 20)

    return(km.res$cluster)
}