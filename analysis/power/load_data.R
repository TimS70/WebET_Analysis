kTrial = 3
nsubj = 20

load_data <- function(kTrial, nsubj) {

    data <- data.frame(
        # For each subject
        subj   = rep(factor(1:nsubj), each=2*kTrial),
        light  = rep(floor(runif(nsubj, 0, 1)+0.5), each=2*kTrial),
        ethnic = rep(floor(runif(nsubj, 0, 2.99)), each=2*kTrial),
        glasses = rep(rep(c(0, 1), each=2*kTrial), each=nsubj/2),
        visualAid = rep(rep(c(1:4), each=2*kTrial), nsubj/4),

        # For each trial
        trial  = rep(1:kTrial, 2*nsubj),
        fps    = 10+rnorm(2*nsubj*kTrial, mean=4, sd=6.68),
        offset = round(rnorm((2*nsubj*kTrial), mean=0.15, sd=0.15), digits=2),
        chin   = rep(c(0, 1), each=kTrial, nsubj)
    )

    data$visualAid <- factor(data$visualAid, levels = c(1, 2, 3, 4),
                             labels = c("noCorrect", "short", "long", "progressive"))
    data$visualAid <- relevel(data$visualAid, ref = "noCorrect")
    data$ethnic <- factor(data$ethnic, levels = c(0, 1, 2),
                          labels = c("Cauc", "Black", "Asian"))
    data$ethnic <- relevel(data$ethnic, ref = "Cauc")
    data$fps_c <- scale(data$fps)
    data$light_c <- scale(data$light)

    return(data)
}