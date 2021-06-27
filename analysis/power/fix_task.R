source(file=file.path('utils', 'get_package.R'))
source(file='load_data.R')

get_package(c(
    "knitr",
    "simr",
    "dplyr",
    "rsq",
    "tictoc",
    "tinytex")
)

# Random Slope Model
model_fix_task <- function(chin_effect) {
    # Intercept and slopes for intervention, time1, time2,     intervention:time1, intervention:time2
    # Effects based on Semmelmann & Weigelt, 2018 - We take the other effects * 3
    fixed <- c(0.15,   # Intercept
               0.001,  # Trial
               chin_effect,   # chin
               0.02, # glasses
               0.005, # short
               0.005, # long
               0.001, # progressive
               0.0007, # Black
               0.007   # Asian
    )

    # Random intercepts for participants clustered by class, Variance from above
    # https://rstudio-pubs-static.s3.amazonaws.com/484106_6b51212f20164fdd88cd7cce89bdef79.html
    rand <- matrix(c(0.05^2, -0.0005, -0.0005, 0.03^2), 2, 2)
    # Extract residual sd
    res <- (1.218e-12^0.5)
    m <- makeLmer(offset ~ trial + chin + glasses + visualAid + ethnic  + (1 + chin |subj),
                  fixef=fixed, VarCorr=rand, sigma=res, data=ds)

    return(m)
}

simulate_fix_task <- function(chin_effect,
                              myNSim,
                              myBreaks,
                              n_min,
                              n_max) {

    output <- list(rep(0, length(chin_effect)))

    for(i in seq_along(chin_effect)) {
        m <- model_fix_task()
        m <- extend(m, along="subj", n=500)
        pc <- powerCurve(m, along="subj",
                 test = fixed("glasses", method="t"),
                 breaks=seq(n_min, n_max, myBreaks),
                 nsim=myNSim)
        output[[i]] <- list(m, pc)
        names(output[[i]]) <- c("Model", "Power Curve")
    }

    print(output)

    return(output)
}