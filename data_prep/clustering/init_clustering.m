function init_clustering(n_clusters, aoi_width, aoi_height)
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
cd('C:\Users\User\GitHub\WebET_Analysis\data_prep\clustering')

f = waitbar(0,'Reading data');

root = 'C:\Users\User\GitHub\WebET_Analysis';
data = readtable(fullfile(root, 'data', 'choice_task', 'added_var', ...
    'data_et.csv'));

data = data(:, {'run_id', 'trial_index', 'withinTaskIndex', ...
    'x', 'y', 't_task'});

set(0,'DefaultFigureVisible','off');

subject = unique(data.run_id);
separate_clustering_overview = zeros(size(subject, 1), 2);

for i = 1:length(subject)
    
    waitbar(i/length(subject),f,'Looping over subjects');
    data_this_subject = data(data.run_id==subject(i), :);
    [ET_adj_this_subject, separate_clustering] = adjust_clusters(...
        data_this_subject, n_clusters, ...
        aoi_width, aoi_height, ...
        true);
    
    separate_clustering_overview(i, :) = [subject(i), separate_clustering];
    
    ET_adj = [ET_adj; ET_adj_this_subject]; %#ok<AGROW>
    
end

separate_clustering_overview

n_subj_sep = sum(separate_clustering_overview(:, 2));
n_subj_sep_prop = n_subj_sep/length(separate_clustering_overview);
strcat(...
    {'n='}, ...
    int2str(n_subj_sep), ...
    {' ('}, sprintf('%.2f', n_subj_sep_prop), {'%) '}, ...
    {' runs required separate clustering. '})

sep_clust_output = array2table(separate_clustering_overview);
sep_clust_output.Properties.VariableNames(1:2) = {...
    'run_id', 'separate_clustering'};
path = fullfile(...
    'C:\Users\User\GitHub\WebET_Analysis', ...
    'results', 'tables', 'clustering')
mkdir(path);
writetable(sep_clust_output, fullfile(path, 'separate_clustering.csv'));
 
waitbar(1,f,'Writing data');

ET_adj(ET_adj(:,1)==0,:)=[]; %Get rid of points not in AOI
   
%Save output
output = array2table(ET_adj);
output.Properties.VariableNames(1:7) = {...
    'run_id', 'trial_index', 'withinTaskIndex', ...
    'x', 'y', 't_task', 'aoi'};

mkdir(fullfile(...
    'C:\Users\User\GitHub\WebET_Analysis', ...
    'data', 'choice_task', 'cluster_corrected'));

writetable(output, fullfile(...
    'C:\Users\User\GitHub\WebET_Analysis', ...
    'data', 'choice_task', 'cluster_corrected', 'data_et.csv'));

close(f)
end