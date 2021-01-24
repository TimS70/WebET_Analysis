pwd = 'C:\Users\User\GitHub\WebET_Analysis\amasino_dataPrep';
fit_discount_k()
% ET_adjustClusters() 
% Umgehe clustering
dataPath=pwd;
cd(dataPath)
load('data_source/schneegansEtAl_ET.csv')
cd(strcat(dataPath, '\intermediateCSVs'))
csvwrite('ET_adj.csv', schneegansEtAl_ET)
cd(dataPath)

subjectiveValue()
%ET_errorAnalysis()
%numErrors()
