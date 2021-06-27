# Title     : TODO
# Objective : TODO
# Created by: schne
# Created on: 6/27/2021

source('fix_task.R')

tic("total")

# Do not show progress bar
simrOptions("progress"=FALSE)

## Power
simulate_fix_task(chin_effect = c(0.015, 0.02),
                  myNSim = 50,
                  myBreaks = 25,
                  n_min = 200,
                  n_max = 300)

toc()