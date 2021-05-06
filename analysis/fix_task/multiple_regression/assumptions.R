test_assumptions <- function(model, data, path) {
	dir.create(path, showWarnings = F)
	# Global test of model assumptions
	# gvmodel <- gvlma(model)
	# summary(gvmodel) 
	# outliers(model=model, data=data)

	multicollinearity(model=model)
	linearity(model=model, path=path)
	normality(model=model, path=path)
	homoscedasticity(model=model, path=path)

	autocorrelation(model=model)
}

outliers <- function(model, data) {
	# Assessing Outliers
	print(outlierTest(model)) # Bonferonni p-value for most extreme obs
	plot(model, which=1)
	plot(model, which=2)
	plot(model, which=3)
	leveragePlots(model) # leverage plots

	# Influential Observations
	# added variable plots
	my_plot <- avPlots(model)
	print(my_plot)
	
	# Cook's D plot
	# identify D values > 4/(n-k-1)
	cutoff <- 4/((nrow(data)-length(model$coefficients)-2))
	my_plot <- plot(model, which=4, cook.levels=cutoff)
	print(my_plot)
	
	# Influence Plot
	my_plot <- influencePlot(model, 
			  id.method="identify", 
			  main="Influence Plot", 
			  sub="Circle size is proportial to Cook's Distance" )
	print(my_plot)
}

normality <- function(model, path) {
	# Normality of Residuals
	# qq plot for studentized resid
	# distribution of studentized residuals
	sresid <- studres(model)
	png(file = file.path(path, 'normality.png'))
	
	hist(sresid, freq=FALSE, breaks=15,
	   main="Distribution of Studentized Residuals")
	
	xfit<-seq(min(sresid),max(sresid),length=40)
	yfit<-dnorm(xfit)
	lines(xfit, yfit)
	
	dev.off()
}

homoscedasticity <- function(model, path) {
	# Evaluate homoscedasticity
	# non-constant error variance test
	print(ncvTest(model))
	# plot studentized residuals vs. fitted values
	png(file = file.path(path, 'homoscedasticity.png'))
	print(spreadLevelPlot(model))
	dev.off()
}

multicollinearity <- function(model) {
		# Evaluate Collinearity
	print(vif(model)) # variance inflation factors
	print(sqrt(vif(model)) > 2) # problem?
}

linearity <- function(model, path) {
		# Evaluate Nonlinearity
	# component + residual plot
	png(file = file.path(path, 'linearity.png'))
	my_plot <- crPlots(model)
	print(my_plot)
	dev.off()
}

autocorrelation <- function(model) {
	# Test for Autocorrelated Errors
	print(durbinWatsonTest(model))
}
