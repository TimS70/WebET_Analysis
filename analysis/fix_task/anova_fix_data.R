anova_fix_data <- function(data_subject) {
	summary(aov(data_subject$offset ~ data_subject$gender))
	summary(aov(data_subject$offset ~ data_subject$degree))
	summary(aov(data_subject$offset ~ data_subject$ethnic))
	
	summary(aov(data_subject$precision ~ data_subject$gender))
	summary(aov(data_subject$precision ~ data_subject$degree))
	summary(aov(data_subject$precision ~ data_subject$ethnic))
	
	summary(aov(data_subject$hit_ratio ~ data_subject$gender))
	summary(aov(data_subject$hit_ratio ~ data_subject$degree))
	summary(aov(data_subject$hit_ratio ~ data_subject$ethnic))
}