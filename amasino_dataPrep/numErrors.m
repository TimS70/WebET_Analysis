function numErrors()

% Written by Dianna Amasino
% Finds the number of errors per subject, with errors defined as trials in 
% which choice went against subject value based on fitted k 

%Input: sample = 1 for primary sample, 2 for replication, behavioral data,
%subjective value data, discount rate output
%Output: file with the number of errors per subject

dataPath=pwd; %adapt to your location
cd(dataPath)

load('data_source/schneegansETAl_behavior.csv') %load primary sample data
data=schneegansETAl_behavior;
load('intermediateCSVs/subjVals.csv')
load('intermediateCSVs/allLogk.csv')

subj = unique(data(:, 1));
for i = 1:length(subj)  %loop over all subjects
    if ~isnan(allLogk(i))
        sub=find(data(:,1)==subj(i));       
        sv=subjVals(sub,2)>subjVals(sub,3); %If LL>SS = 1, if SS>LL = 0
        errors=find(sv~=data(sub,6) & ~isnan(data(sub,7)) & data(sub,2)<10); %exclude non-responses, trial where immed opt=10   
        %Find total # of errors
        numErrs(i)=length(errors);
        
    else
        numErrs(i)=NaN;
    end
end  

cd(strcat(dataPath, '\intermediateCSVs'))
csvwrite('numErrs.csv',numErrs')
cd(dataPath)
end