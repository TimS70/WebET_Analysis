root = "C:/Users/TimSchneegans/Documents/github/WebET_Analysis"
setwd(root)

source(file.path('utils', 'r', 'get_packages.R'))

get_packages(c(
    "knitr",
    "simr",
    "dplyr",
    "rsq",
    "tictoc",
    "tinytex"
))

tic("total")

simrOptions("progress"=FALSE) # Do not show progress bar
options(scipen=999) # Show R markdown output as Integers
simrOptions(progress=TRUE) #simr setting

myNSim = 25
myBreaks = 100

# reaction time, trial, et indices
path = file.path(root, 'data', 'choice_task', 'cleaned')
data = read.csv(file.path(path, 'data_trial.csv'))

data$rt <- data$trial_duration_exact
data$rt_c <- scale(data$rt)

fixed <- c(1.04,   # Intercept
           0.0076, # Trial
           -0.393, # rt
           -0.07, # et_index
           -0.07, # et_index
           -0.07 # et_index
)

# Random intercepts for participants clustered by class, Variance from above
# https://rstudio-pubs-static.s3.amazonaws.com/484106_6b51212f20164fdd88cd7cce89bdef79.html
rand <- 1.40
      # matrix(c(-0.58, 0.48, -0.99, 
      #            0.48, 0.44, 0.66,
      #            -0.99, 0.66, -0.38), 3, 3)

m <- glmer(choseLL ~ withinTaskIndex + rt_c + 
                  optionIndex + attributeIndex + payneIndex + (1 | run_id), 
               family='binomial', 
               data=data)

powerSim(m, test = fixed("optionIndex", method="t"), nsim=myNSim)




m <- extend(m, along="run_id", n=500)
pc <- powerCurve(m, along="run_id", 
                 test = fixed("et_index_1", method="t"), 
                 breaks=seq(150, 300, myBreaks), 
                 nsim=myNSim)

fixef(m)['optionIndex'] <- 0.17
fixef(m)['attributeIndex'] <- 0.07
fixef(m)['payneIndex'] <- 0.07

toc()