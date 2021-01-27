pwd = 'C:\Users\User\GitHub\WebET_Analysis\amasino_dataPrep';
fit_discount_k()
% ET_adjustClusters() 
% Umgehe clustering
dataPath=pwd;
cd(dataPath)
load('data_source/schneegansEtAl_ET.csv')
data = schneegansEtAl_ET
data = data(:, 3

test = data(data(:, 3)>((0.05+0.9*0.2)-0.15) & data(:, 3)<((0.05+0.9*0.2)+0.15), :)

% col 3: x-position (pixels on screen)
% col 4: y-position (pixels on screen)

cd(strcat(dataPath, '\intermediateCSVs'))
csvwrite('ET_adj.csv', data)
cd(dataPath)

%ET_errorAnalysis()
%numErrors()
