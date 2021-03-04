function init_clustering()
% Original version written by Dianna Amasino 2016
% Updated by Dianna Amasino 2019 based on edits made by Khoi Vo, 2016
% Adapted by Tim Schneegans 2020
% Huettel lab, Duke University

% This function takes in eye tracking data as gaze points predicted by 
% Webgazer and extracted from the choice period of trials and adjusts it so that the 
% clusters relating to each AOI are properly centered (accounting for bad 
% calibration or calibration drift over the course of the experiment. 

% It does this by:
% 1) Fitting clusters of the data.
% 2) Identifying clusters at the 4 corners (which excludes clusters left 
% over from fixation).
% 3) Moving the clusters such that the center of mass of the cluster is 
% centered in the AOI.

% INPUT
% col 1: subject number (matching behavioral data)
% col 2: Trial number
% col 3: x-position (pixels on screen)
% col 4: y-position (pixels on screen)
% col 5: time

% Output
% col 1: subject number (matching behavioral data)
% col 2: Trial number
% col 3: x-position (pixels on screen)
% col 4: y-position (pixels on screen)
% col 5: time
% col 6: AOI {'TL'; 'TR'; 'BL'; 'BR'}

ET_adj=[]; % All corrected eye-tracking data

%Load data
cd('C:\Users\User\GitHub\WebET_Analysis\clustering')

f = waitbar(0,'Reading data');

data = readtable('..\data_jupyter\choice_task\data_et.csv');
data = data(:, {'run_id', 'withinTaskIndex', ...
    'x', 'y', 't_task'});

set(0,'DefaultFigureVisible','off');

subject = unique(data.run_id);

for i = 1:length(subject)
    
    waitbar(i/length(subject),f,'Looping over subjects');
    data_this_subject = data(data.run_id==subject(i), :);
    ET_adj_this_subject = adjust_clusters(data_this_subject, 12, 0.30, 0.30);
    ET_adj = [ET_adj; ET_adj_this_subject]; %#ok<AGROW>
    
end

waitbar(1,f,'Writing data');

ET_adj(ET_adj(:,1)==0,:)=[]; %Get rid of points not in AOI
   
%Save output
output = array2table(ET_adj);
output.Properties.VariableNames(1:6) = {...
    'run_id', 'withinTaskIndex', ...
    'x', 'y', 't_task', 'aoi'};
writetable(output, '../data_jupyter/choice_task/data_et_adjusted.csv');

close(f)
end