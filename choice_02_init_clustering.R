setwd("C:/Users/User/GitHub/WebET_Analysis/clustering")

getPackages <- function(pkg){
  new.pkg <- pkg[!(pkg %in% installed.packages()[, "Package"])]
  if (length(new.pkg)) 
    install.packages(new.pkg, dependencies = TRUE)
  sapply(pkg, require, character.only = TRUE)
}

getPackages('matlabr')

system('matlab -nodesktop -nosplash -r "init_clustering(14, 0.3, 0.3); exit"')

setwd("C:/Users/User/GitHub/WebET_Analysis")
