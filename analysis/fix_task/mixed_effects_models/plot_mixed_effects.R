library(ggplot2)
library(reghelper)
library(gridExtra)
library(sjPlot)
library(sjmisc)
library(lme4)
library(lattice)

plot_random_intercepts <- function(data) {
    
    theme_set(theme_bw(base_size = 10, base_family = ""))
    
    Active.Plot <-ggplot(data = data, aes(x = chin, y=offset))+
        coord_cartesian(ylim=c(0, 100))+
        geom_point()+
        geom_smooth(method = "lm", se = TRUE)+
        xlab("Chin Rest")+ylab("Offset")+
        theme(legend.position = "none")
    
    Size.Plot <-ggplot(data = data, aes(x = glasses_binary, y=offset))+  
        coord_cartesian(ylim=c(0, 100))+
        geom_point()+
        geom_smooth(method = "lm", se = TRUE)+
        xlab("Glasses")+ylab("Offset")+
        theme(legend.position = "top")
    
    my_plot <- grid.arrange(Size.Plot, Active.Plot, ncol=2)
    
    print(my_plot)
    
}

plot_random_intercepts(data=data)

# Random Slopes with predictions

plot_random_slopes <- function(data, model, y_max=100) {
    
    data$offset_prediction <- predict(model, newdata=data)
    
    sd_chin <- 7.1245
    sd_intercept <- 6.3808
    
    theme_set(theme_bw(base_size = 10, base_family = ""))
    
    plot_a <-ggplot(data = data, aes(x = chin, y=offset, group=run_id))+
        coord_cartesian(ylim=c(0, y_max))+
        geom_smooth(method = "lm", se = FALSE, color='grey69') +
        #geom_point(colour = 'gray45')+
        geom_segment(aes(x=0, 
                         xend=1, 
                         y=summary(model)$coef[1],
                         yend=summary(model)$coef[1]+summary(model)$coef[6]),
                     size=1
        ) + 
        geom_segment(aes(x=0, 
                         xend=1, 
                         y=summary(model)$coef[1] - sd_intercept,
                         yend=summary(model)$coef[1]-sd_intercept+(summary(model)$coef[6]-sd_chin)),
                     size=1
        ) + 
        geom_segment(aes(x=0, 
                         xend=1, 
                         y=summary(model)$coef[1] + sd_intercept,
                         yend=summary(model)$coef[1]+sd_intercept+(summary(model)$coef[6]+sd_chin)),
                     size=1
        ) + 
        xlab("Chin Rest")+ylab("Offset")+
        theme(legend.position = "none")
    
    
    plot_b <-ggplot(data = data, aes(x = chin, y=offset_prediction, group=run_id))+
        coord_cartesian(ylim=c(0, y_max))+
        geom_smooth(method = "lm", se = FALSE, color='grey69')+
        #geom_point(colour = 'gray45')+
        geom_segment(aes(x=0, 
                         xend=1, 
                         y=summary(model)$coef[1],
                         yend=summary(model)$coef[1]+summary(model)$coef[6]),
                     size=1
                    ) + 
        geom_segment(aes(x=0, 
                         xend=1, 
                         y=summary(model)$coef[1],
                         yend=summary(model)$coef[1]+(summary(model)$coef[6]-sd_chin)),
                     size=1
                     ) + 
        geom_segment(aes(x=0, 
                         xend=1, 
                         y=summary(model)$coef[1],
                         yend=summary(model)$coef[1]+(summary(model)$coef[6]+sd_chin)),
                     size=1
                     ) + 
        xlab("Chin Rest")+ylab("Offset Prediction")+
        theme(legend.position = "none")
    
    my_plot <- grid.arrange(plot_a, plot_b, ncol=2)
 
    print(my_plot)
}

plot_random_slopes(data=data_trial, model=lmer_offset, y_max=50)

data = data_trial
model = lmer_offset

summary(model)$var
# Plot Random effects
dotplot(ranef(model))

ranef(model, condVar = TRUE)

data_random_effects <- as.data.frame(ranef(model))
chin_var <- data_random_effects %>%
    filter(term=='chin') %>%
    dplyr::pull(condval)

sd(chin_var)

ranef(model)
summary(model)$var
