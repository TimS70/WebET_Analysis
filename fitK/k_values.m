cd('C:\Users\User\GitHub\WebET_Analysis\fitK')
data = readtable('fit_k_input.csv');

subjects = unique(data.run_id);
output = zeros(length(subjects), 3);

for i = 1:length(subjects)
    data_thisSubject = data(data.run_id==subjects(i), :);
    [k, logLik] = fitK(data_thisSubject);
    
    output(i, :) = [unique(data_thisSubject.run_id), log(k), logLik];  
end

output = array2table(output);
output.Properties.VariableNames(1:3) = {'run_id','logK','logLik'};
writetable(output, 'k_values.csv')
