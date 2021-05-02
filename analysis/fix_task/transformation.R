
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


data_trial = data_trial %>%
    mutate(
        offset_log = log(offset+1),
        offset_log10 = log10(offset+1),
        offset_sqrt = sqrt(offset),
        )

lmer_log = lmer(
    offset_log ~ y_pos_c + chin + (chin | run_id), 
    data=data_trial,
    REML=FALSE)
summary(lmer_log)
# ranef(lmer_log)
qqmath(lmer_log, id=0.05, prep_global_data='log transformed offset')

lmer_log10 = lmer(
    offset_log10 ~ y_pos_c + chin + (chin | run_id), 
    data=data_trial,
    REML=FALSE)
summary(lmer_log10)
# ranef(lmer_log10)
qqmath(lmer_log10, id=0.05, prep_global_data='log10 transformed offset')

lmer_sqrt = lmer(
    offset_sqrt ~ y_pos_c + chin + (chin | run_id), 
    data=data_trial,
    REML=FALSE)
summary(lmer_sqrt)
# ranef(lmer_sqrt)
qqmath(lmer_sqrt, id=0.05, prep_global_data='sqrt transformed offset')


data_trial = data_trial %>%
    mutate(
        res = residuals(lmer_sqrt),
        res_sq = (abs(res)^2))

levene_model <- lm(res_sq ~ run_id, data=data_trial)
anova(levene_model)

plot(lmer_sqrt)