function subjectiveValue()

% Written by Dianna Amasino
% Finds the trial by trial subject value of the smaller, sooner (SS) and 
% larger, later (LL) options and of the left and right options based on 
% each individual subject's fitted discount rate, k.
% Also splits trials into 10 bins by difference in subjective value (SV) between 
% the left and right options and finds the proportion of left responses,
% the response times, and the number of fixations for each SV bin.

%Input: 
% behavioral data
% col 1: 'run_id'
% col 2: 'aSS'
% col 3: 'aLL'
% col 4: 'tSS'
% col 5: 'tLL'
% col 6: 'choseLL'
% col 7: 'rt'
% col 8: 'LL_top',
% col 9: 'choseTop'
%discount rates, and number of fixations per trial per subject. 

%Output: 
% subjVals.csv
% Col 1: subject ID
% Col 2: SV of the LL option
% Col 3: SV of the SS option
% Col 4: SV of the top option 
% Col 5: SV of the bottom options. 

% proportion of to choices (SVpropT.csv),
%the average response time (SVrt.csv) for SV left - SV right option value bins from [-10, 10].

dataPath=pwd; %adapt to your location
cd(dataPath)

load('data_source/schneegansETAl_behavior.csv')
load('intermediateCSVs/allLogk.csv')
data=schneegansETAl_behavior;
logk=allLogk;
    
subj = unique(data(:, 1));
for i = 1:length(subj)  %loop over all subjects

    k=exp(logk(i));
    rows=find(data(:,1)==subj(i));
    svLL(rows,1)=data(rows,3)./(1+k.*data(rows,5));
    svSS(rows,1)=data(rows,2)./(1+k.*data(rows,4));

    rows0=find(data(rows,8)==0); % (side == 1) means LL on top, SS on bottom
    rows1=find(data(rows,8)==1);

    svLT(rows(rows0),1)=svSS(rows(rows0)); % Subjective value Top
    svRB(rows(rows0),1)=svLL(rows(rows0)); % Subjective value bottom 
    svLT(rows(rows1),1)=svLL(rows(rows1)); % Subjective value Top
    svRB(rows(rows1),1)=svSS(rows(rows1)); % Subjective value bottom 
    dSV(rows,1)=svLT(rows)-svRB(rows); %Difference in subjective value (Left - right or Top - bottom)
    
    %Put values into 5 bins of SV Top - SV bottom bins 
    for j=1:5; %for range of SV left - SV right is (-5,5) in increments of 2   
        ind=find(dSV(rows)>=(-7+2*j) & dSV(rows)<(-5+2*j)); 
        propT(j)=mean(data(rows(ind),9)); %Find proportion of top choices
        rt(j)=mean(data(rows(ind),7)); %find RT
    end
    SVpropT(i,:)=[i propT];
    SVrt(i,:)=[i rt];
end   

subjVals=[data(:,1) svLL svSS svLT svRB dSV];

cd(strcat(dataPath, '\intermediateCSVs'))
csvwrite('subjVals.csv',subjVals) % write log subjective values to csv
csvwrite('SVpropT.csv',SVpropT)
csvwrite('SVrt.csv',SVrt)
cd(dataPath)
end