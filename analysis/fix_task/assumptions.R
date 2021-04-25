# Sources: 
# https://www.youtube.com/watch?v=UvyxSqEXBwc
# https://www.pythonfordatascience.org/mixed-effects-regression-python/
# https://ademos.people.uic.edu/Chapter18.html
# https://cran.r-project.org/web/packages/DHARMa/vignettes/DHARMa.html

set.seed(8675309)

source(file.path(root, 'utils', 'r', 'merge_by_subject.R'))
source(file.path(root, 'utils', 'r', 'get_packages.R'))
get_packages(c(
		"lme4",
		"ggplot2",
		"HLMdiag",
		"DHARMa",
		"car", #for the Levene test which we will not discuss here
		"Matrix"))

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
lmer_offset = glmer(
    offset_100 ~ withinTaskIndex + x_pos_c + y_pos_c + fps + chin + glasses_binary + 
    	(chin + glasses_binary | run_id), 
    data=data_trial,
    family='poisson')
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

# Over- Underdispersion
testDispersion(simulation_output)
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


# resid() calls for the residuals of the model, Cigarettes was our initial 
# outcome variables - we're plotting the residuals vs observered

Plot.Model.F.Linearity<-plot(resid(Model.F),Cigarettes) 


sessionInfo()
