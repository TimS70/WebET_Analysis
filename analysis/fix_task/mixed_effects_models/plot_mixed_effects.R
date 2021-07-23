data <- data_trial
model <- lmer_offset

path <- file.path(getwd(), 'results', 'plots', 'fix_task', 'mixed_effects')
dir.create(path)

library(ggplot2)
library(reghelper)
library(gridExtra)
library(lattice)
library(tidyverse) #for all data wrangling
library(cowplot) #for manuscript ready figures
library(lme4) #for lmer & glmer models
library(sjPlot) #for plotting lmer and glmer mods
library(sjmisc)
library(effects)
library(sjstats) #use for r2 functions

theme_set(theme_bw(base_size = 20, base_family = ""))

# Random Slopes with predictions
grouped <- data_trial %>% group_by(run_id, chin) %>%
        dplyr::summarise(
            offset=mean(offset),
            .groups='keep'
            )

for (run in data_trial$run_id %>% unique()) {
    grouped[(grouped$run_id == run) & (grouped$chin == 1), 'offset'] <-
        grouped[(grouped$run_id == run) & (grouped$chin == 0), 'offset'] + summary(model)$coef[6]
}

# Random Intercept, Fixed effect
plot_rifs <- ggplot(data = grouped, aes(x = factor(chin), y=offset, group = run_id)) +
    coord_cartesian(ylim=c(0, 100)) +
    geom_line(color='#CCCCCC') + # (method = "lm", se = FALSE, color='black') +
    geom_segment(aes(
            x=factor(0),
            xend=factor(1),
            y=summary(model)$coef[1],
            yend=summary(model)$coef[1] + (summary(model)$coef[6])),
        size=1,
        colour='red')
ggsave(filename=file.path(path, 'mod_fifs.png'))

data_ribbon <- data.frame(chin = 0:10 / 10) %>%
    mutate(
        outcome=summary(model)$coef[1] + summary(model)$coef[6] * chin,
        lower=outcome-sd_intercept,
        upper=outcome+sd_intercept)

# Random Intercept, Fixed effect Ribbons
sd_intercept <- 6.3808

plot_rifs_ribbon <- ggplot(data = data_ribbon, aes(x = chin, y=outcome)) + # , group = run_id)) +
    coord_cartesian(ylim=c(0, 100)) +
    geom_ribbon(aes(ymin=lower,
                    ymax=upper),
                colour='#CCCCCC'
    ) +
    geom_point(data=data_trial,
               aes(x = chin, y=offset, group = run_id),
               colour='black') +
    geom_line(data = data_ribbon, aes(x = chin, y=outcome),
              colour='red',
              size=1)
ggsave(filename=file.path(path, 'mod_rifs_ribbon.png'))

# Random Slope Fixed Intercept
sd_chin <-  7.1245
fix_chin <- summary(model)$coef[6]
fix_intercept <- summary(model)$coef[1]
data$outcome_prediction <- predict(model, newdata=data)

plot_firs <- ggplot(data=data, aes(x = chin, y=offset)) + # , group = run_id)) +
    coord_cartesian(ylim=c(0, 100), xlim=c(0, 1)) +
    geom_abline(slope = seq(fix_chin-sd_chin, fix_chin+sd_chin, 0.001),
                intercept = fix_intercept,
                color = '#CCCCCC') +
    geom_abline(slope = fix_chin,
                intercept = fix_intercept,
                color = "red") +
    geom_point(data=data_trial,
               aes(x = chin, y=offset, group = run_id),
               colour='black')
    # facet_grid(.~glasses_binary) +
ggsave(filename=file.path(path, 'mod_fifs.png'))

# Random Slope Random Intercept Lines
grouped <- data_trial %>% group_by(run_id, chin) %>%
        dplyr::summarise(
            offset=mean(offset),
            .groups='keep'
            )

plot_rirs_lines <- ggplot(data = grouped, aes(x = factor(chin), y=offset, group = run_id)) +
    coord_cartesian(ylim=c(0, 100)) +
    geom_line(color='#CCCCCC') + # (method = "lm", se = FALSE, color='black') +
    geom_segment(aes(
            x=factor(0),
            xend=factor(1),
            y=summary(model)$coef[1],
            yend=summary(model)$coef[1] + (summary(model)$coef[6])),
        size=1,
        colour='red')
ggsave(filename=file.path(path, 'mod_rirs_line.png'))

# Random Slope Random Intercept Ribbon
fix_intercept <- summary(model)$coef[1]
sd_intercept <- 6.3808
fix_chin <- summary(model)$coef[6]
sd_chin <-  7.1245

plot_rirs_ribbon <- ggplot(data = grouped, aes(x = chin, y=offset, group = run_id)) +
    coord_cartesian(ylim=c(0, 100)) +
    geom_abline(slope = seq(fix_chin-sd_chin, fix_chin+sd_chin, 0.001),
                intercept = fix_intercept, # seq(fix_intercept-sd_intercept, fix_intercept+sd_intercept, 0.001),
                color = '#CCCCCC') +
    geom_abline(slope = fix_chin+sd_chin,
            intercept = seq(fix_intercept-sd_intercept, fix_intercept+sd_intercept, 0.001),
            color = '#CCCCCC') +
    geom_abline(slope = fix_chin-sd_chin,
            intercept = seq(fix_intercept-sd_intercept, fix_intercept+sd_intercept, 0.001),
            color = '#CCCCCC') +
    geom_abline(slope = fix_chin,
                intercept = fix_intercept,
                color = "red") +
    geom_point()
ggsave(filename=file.path(path, 'mod_rirs_ribbon.png'))

my_plot <- grid.arrange(plot_rifs_ribbon, plot_firs, plot_rirs_ribbon, ncol=3)
print(my_plot)


# Plot the fixed effect sizes
sjPlot::plot_model(
    model,
    title='Effects of Variables on Offset',
    axis.labels=c('Trial', 'x-Position', 'y-Position', 'Frame rate', 'Chin rest', 'Glasses'),
    show.values=TRUE, show.p=TRUE
) + font_size(labels.x = 15, labels.y = 15)
path <- file.path(getwd(), 'results', 'plots', 'fix_task', 'mixed_effects')
dir.create(path)
ggsave(filename=file.path(path, 'fixed_effects.png'))

# Plot model estimates
lmer_offset_ri <- offset_models(data=data_trial, get_ci=FALSE, output_model = 'random_intercept')

# Split Violin
my_plot <- ggplot(data=data, aes(factor(chin), offset, fill = factor(glasses_binary))) +
    geom_split_violin()
ggsave(filename=file.path(path, 'split_violin.png'))


summary(model)$var
# Plot Random effects
dotplot(ranef(model))

ranef(model, condVar = TRUE)



sd(chin_var)

ranef(model)
summary(model)$var

# goals: grafischen Vergleich von fixed effects, random Intercept, random slope und random intercept & slope
# geom_ribbon als simple slopes

    # data_random_effects <- as.data.frame(ranef(model))
    # run_intercepts <- data_random_effects %>%
    #     filter(term==('(Intercept)')) %>%
    #     dplyr::pull(condval)

    # plot_ri <-ggplot(data = data, aes(x = chin, y=offset, group=run_id))+
    #     coord_cartesian(ylim=c(0, y_max))+
    #     geom_smooth(method = "lm", se = FALSE, color='grey69') +
    #     #geom_point(colour = 'gray45')+
    #
    #     geom_segment(aes(x=0,
    #                      xend=1,
    #                      y=summary(model)$coef[1] - sd_intercept,
    #                      yend=summary(model)$coef[1]-sd_intercept+(summary(model)$coef[6]-sd_chin)),
    #                  size=1
    #     ) +
    #     geom_segment(aes(x=0,
    #                      xend=1,
    #                      y=summary(model)$coef[1] + sd_intercept,
    #                      yend=summary(model)$coef[1]+sd_intercept+(summary(model)$coef[6]+sd_chin)),
    #                  size=1
    #     ) +
    #     xlab("Chin Rest")+ylab("Offset")+
    #     theme(legend.position = "none")
    #
    #
    # plot_b <-ggplot(data = data, aes(x = chin, y=offset_prediction, group=run_id))+
    #     coord_cartesian(ylim=c(0, y_max))+
    #     geom_smooth(method = "lm", se = FALSE, color='grey69')+
    #     #geom_point(colour = 'gray45')+
    #     geom_segment(aes(x=0,
    #                      xend=1,
    #                      y=summary(model)$coef[1],
    #                      yend=summary(model)$coef[1]+summary(model)$coef[6]),
    #                  size=1
    #                 ) +
    #     geom_segment(aes(x=0,
    #                      xend=1,
    #                      y=summary(model)$coef[1],
    #                      yend=summary(model)$coef[1]+(summary(model)$coef[6]-sd_chin)),
    #                  size=1
    #                  ) +
    #     geom_segment(aes(x=0,
    #                      xend=1,
    #                      y=summary(model)$coef[1],
    #                      yend=summary(model)$coef[1]+(summary(model)$coef[6]+sd_chin)),
    #                  size=1
    #                  ) +
    #     xlab("Chin Rest")+ylab("Offset Prediction")+
    #     theme(legend.position = "none")
    #
    # my_plot <- grid.arrange(plot_a, plot_b, ncol=2)
    #
    # print(my_plot)