function ET_adjustClusters()
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
% col 6: window width (pixels on screen)
% col 7: window height (pixels on screen)

% Output
% col 1: subject number (matching behavioral data)
% col 2: Trial number
% col 3: x-position (pixels on screen)
% col 4: y-position (pixels on screen)
% col 5: time
% col 6: AOI {'TL'; 'TR'; 'BL'; 'BR'}

ET_adj=[];

%Load data
dataPath=pwd; %adapt to your location
cd(dataPath)
load('data_source/schneegansEtAl_ET.csv')
data=schneegansEtAl_ET;
subj = unique(data(:, 1));

for i = 1:length(subj)
    adjET=[];
    adjET1=[];
    adjET2=[];

    sub = data(:,1)==subj(i); % subject-specific data points
    grandmean=mean(data(sub,3:4)); %Find center of all eye data points
    
    aoiSizePercentage = 0.3;
    screen_width = max(data(sub, 6));
    screen_height = max(data(sub, 7));
    corners = {'TL'; 'TR'; 'BL'; 'BR'};

    % Create Plot
    savePlot(data(sub, 3), data(sub, 4), screen_width, screen_height, 'plots/BeforeCorrection_FIG%d.png', i);

    sub = data(:,1)==subj(i); % subject-specific data points
    [dataWithClusters, aoiInfo, clusterInfo, matchedClusterInd] = getClusters(data(sub, :), ...
        grandmean, aoiSizePercentage, screen_width, screen_height);
   
    % Separate clustering for first and second half of the experiment
    sub1 = data(:,1)==subj(i) & data(:,2)<41;
    [dataWithClusters1, aoiInfo1, clusterInfo1, matchedClusterInd1] = getClusters(data(sub1, :), ...
        grandmean, aoiSizePercentage, screen_width, screen_height);
    
    sub2 = data(:,1)==subj(i) & data(:,2)>40;
    [dataWithClusters2, aoiInfo2, clusterInfo2, matchedClusterInd2] = getClusters(data(sub2, :), ...
        grandmean, aoiSizePercentage, screen_width, screen_height);
    
    % Clusters differ if >40 pixels deviation and > 20 gaze points 
    clusters1And2differ  = ...
        sum(sum(abs(clusterInfo1(matchedClusterInd1,3:4)-clusterInfo2(matchedClusterInd2,3:4))>40)) && ...
        sum(clusterInfo1(matchedClusterInd2, 1)>20) && ...
        sum(clusterInfo2(matchedClusterInd2, 2)>20);
    
   if clusters1And2differ
        'Need some new code here!'
   end 
   
   for j=1:4 %for each AOI          
       % Find the points within the new cluster 
       thisClusterInd = aoiInfo.(corners{j})(9);
       ind_withinCluster = find(...
               dataWithClusters(:,4)>clusterInfo(thisClusterInd, 5) & ...
               dataWithClusters(:,4)<clusterInfo(thisClusterInd, 6) & ...
               dataWithClusters(:,5)>clusterInfo(thisClusterInd, 7) & ...
               dataWithClusters(:,5)<clusterInfo(thisClusterInd, 8) ...
           );

       % Adjust the x and y position such that cluster center is in middle of AOI
       adjET(ind_withinCluster, 1:6) = ...
           [...
               dataWithClusters(ind_withinCluster, 1:2), ...
               dataWithClusters(ind_withinCluster, 3) + (aoiInfo.(corners{j})(1)-clusterInfo(thisClusterInd, 3)), ...
               dataWithClusters(ind_withinCluster, 4) + (aoiInfo.(corners{j})(2)-clusterInfo(thisClusterInd, 4)) ...
               dataWithClusters(ind_withinCluster, 5), ...
               repmat(j, length(ind_withinCluster),1)...
           ];
   end  
   

   adjET(adjET(:,1)==0,:)=[]; %Get rid of points not in AOIs
   
   savePlot(data(sub, 3), data(sub, 4), screen_width, screen_height, 'plots/AfterCorrection_FIG%d.png', i);
   
   ET_adj=[ET_adj; adjET]; %Add this subject to all subjects
end

%Save output
cd(strcat(dataPath, '\intermediateCSVs'))
csvwrite('ET_adj.csv', ET_adj)
cd(dataPath)
   
end