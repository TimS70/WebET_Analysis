source(file=file.path('analysis', 'power', 'fix_task.R'))

tic(msg="total")

# Do not show progress bar
simrOptions("progress"=TRUE)

simulate_fix_task(
    chin_effect = c(0.02),
    myNSim = 50,
    myBreaks = 50,
    n_min = 200,
    n_max = 300)

toc()

exp(1.165+0.06)
