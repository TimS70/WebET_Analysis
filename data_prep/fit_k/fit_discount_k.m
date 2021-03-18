function fit_discount_k()
%Fits hyperbolic discount rate

%REVISION HISTORY:
%     brian  03.10.06 written
%     brian  03.14.06 added fallback to FMINSEARCH, multiple fit capability
%     kenway 11.29.06 added CI evaluation for FMINSEARCH (which returns
%     Hessian)
%     joe kable 03.12.09 modified to work with revised version of
%     choice_prob and discount
%     khoi 06.26.09 simplified
%     schneegans 08.01.2021 simplified 


root = 'C:\Users\User\GitHub\WebET_Analysis';

cd(fullfile(root, 'data_prep', 'fit_k'));

f = waitbar(0,'Reading data');

data = readtable(fullfile(root, ...
    'data', 'choice_task', 'added_var', 'data_trial.csv'));

data = data(:, {'run_id', 'aSS', 'aLL', 'tSS', 'tLL', ...
    'choseLL', 'trial_duration_exact', 'LL_top', 'choseTop'});

output=[];

subject = unique(data.run_id);
for i = 1:length(subject)  %loop over all subjects
    data_thisSubject = data(data.run_id==subject(i), :);

    [info, p] = fit_discount_model(...
        data_thisSubject.choseLL, ...
        data_thisSubject.aSS, ...
        0, ...
        data_thisSubject.aLL, ...
        data_thisSubject.tLL);
    
    noise = info.b(1);
    k = info.b(2);
    
    if k<.0001 && mean(data_thisSubject.choseLL)>.95 %Extremely patient
        output=[output; subject(i), -9.5, noise];
    elseif k<0 %Inconsistent choice, can't properly fit
        output=[output; subject(i), NaN, noise];
    else %Fit within typical range, keep fit
        output=[output; subject(i), log(k), noise]; %Save log(k) as output
    end
    
    waitbar(i/length(subject),f,'Looping over subjects');
        
end

waitbar(1,f,'Writing data');

output = array2table(output);
output.Properties.VariableNames(1:3) = {
    'run_id', 'logK', 'noise'};

cd(fullfile(root, 'data', 'choice_task'));
writetable(output, 'logK.csv');
cd(root);

close(f)

end




