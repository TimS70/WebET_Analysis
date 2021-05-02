# Sources: 
# https://www.youtube.com/watch?v=UvyxSqEXBwc
# https://www.pythonfordatascience.org/mixed-effects-regression-python/
# https://ademos.people.uic.edu/Chapter18.html
# https://cran.r-project.org/web/packages/DHARMa/vignettes/DHARMa.html

getwd()
set.seed(8675309)

root = 'C:/Users/User/GitHub/WebET_Analysis'
source(file.path(root, 'utils', 'r', 'merge_by_subject.R'))
source(file.path(root, 'utils', 'r', 'get_packages.R'))

get_packages(c(
		'dplyr', 
		"lme4",
		"ggplot2",
		"HLMdiag",
		"DHARMa",
		'robustlmm',
		"car", #for the Levene test which we will not discuss here
		"Matrix"))

library(optimx)

path = file.path(root, 'data', 'fix_task', 'added_var')

# Get Data
data_subject = read.csv(file.path(path, 'data_subject.csv'))
data_trial = read.csv(file.path(path, 'data_trial.csv'))
data_et = read.csv(file.path(path, 'data_et.csv'))

summarize_datasets(data_et, data_trial, data_subject)

data_trial = data_trial %>%
	merge_by_subject(data_subject, 'window') %>%
    mutate(y_pos_c = dplyr::recode(y_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
    	   x_pos_c = dplyr::recode(x_pos, '0.2'=(-1L), '0.5'=0L, '0.8'=1L),
    	   fps_c = scale(fps),
    	   window_c = scale(window))


# Fit models 
data_trial$offset_100 = data_trial$offset * 100
lmer_offset = lmer(
    offset_100 ~ withinTaskIndex + x_pos_c + y_pos_c + fps + chin + glasses_binary + 
    	(chin | run_id), 
    data=data_trial, 
    REML=FALSE)
summary(lmer_offset)

lmer_precision = lmer(
    precision ~ withinTaskIndex + x_pos_c + y_pos_c + fps + chin + glasses_binary + 
    	(chin + glasses_binary | run_id), 
    data=data_trial,
    REML=FALSE)

lmer_hit_mean = lmer(
    hit_mean ~ withinTaskIndex + x_pos_c + y_pos_c + fps + chin + glasses_binary + 
    	(1 | run_id), 
    data=data_trial,
    REML=FALSE)

# Linearity
simulation_output = simulateResiduals(lmer_offset, plot=T, use.u = T)
testDispersion(simulation_output)
simulation_output = simulateResiduals(lmer_precision, plot=T, use.u = T)
testDispersion(simulation_output)
simulation_output = simulateResiduals(lmer_hit_mean, plot=T, use.u = T)

# Over- Underdispersion


# Robust LMM
lmer_offset_r = rlmer(
    offset_100 ~ withinTaskIndex + x_pos_c + y_pos_c + fps + chin + glasses_binary 
    + (chin | run_id),
    	#(chin + glasses_binary | run_id), 
    data=data_trial)
summary(lmer_offset_r) # look at the robustness weights
confint(lmer_offset_r, method="boot", n=50)
plot(lmer_offset) # qq-plot



testQuantiles(simulation_output)



subset = data_trial %>% 
	filter(run_id==unique(data_trial$run_id)[1]) %>% 
	dplyr::select(offset_100)

ggplot(data_trial, aes(x=offset_100)) + 
	geom_histogram(binwidth=25)


# Tested for various predictors 
plotResiduals(simulation_output, data_trial$run_id)

plotResiduals(simulation_output, form = data_trial$run_id)
residuals(simulation_output, quantileFunction = qnorm, outlierValues = c(-7,7))
simulateResiduals(lmer_precision, plot=T, use.u = T)
simulateResiduals(lmer_hit_mean, plot=T, use.u = T)

library(faraway)
data(butterfat)
fullmodel = lm(Butterfat ~ Breed * Age, data = butterfat)
plot(fullmodel)


# Box-Cox 
library(MASS)
bc = boxcox(fullmodel, lambda = seq(-3, 3))
best.lam = bc$x[which(bc$y==max(bc$y))]

fullmodel.inv = lm((Butterfat)^-1 ~ Breed * Age, data=butterfat)
plot(fullmodel.inv)

# Box-Cox mix
library(boxcoxmix)

data(Oxboys, package="nlme")
Oxboys$boy <- gl(26,9)
Oxboys$boy

testox <- np.boxcoxmix(height ~ age, groups = Oxboys$boy, data = Oxboys,
					   K = 3, tol = 1, start = "gq", lambda=1, verbose=FALSE)

test.inv <- np.boxcoxmix(lmer_offset, 
						 groups = data_trial$run_id, 
						 data = data_trial,
						 K = 2, 
						 tol = 1, 
						 start = "gq", 
						 lambda=1, 
						 verbose=FALSE)
plot(test.inv)
test.optim <- optim.boxcox(lmer_offset, 
						   data = data_trial,
						   find.in.range = c(-3, 3))
test.optim
plot(test.optim)
sessionInfo()
