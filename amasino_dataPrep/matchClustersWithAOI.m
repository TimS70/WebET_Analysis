function [aoiInfo, matchedClusterInd] = matchClustersWithAOI(aoiInfo, clusterInfo, grandmean, screen_width, screen_height)  
    

    %Assign clusters to each quadrant of the screen relative to the grandmean as center
    %Clusters should be at least 100 pixels horizontally away from the center to avoid the fixation cluster
    minXDeviation = screen_width * 0.1;
    minYDeviation = screen_height * 0.1;
    
    clusterInd.TL = clusterInfo(~(clusterInfo(:,3)>grandmean(1)-minXDeviation & clusterInfo(:,4)>grandmean(2)-minYDeviation), 1);
    clusterInd.BL = clusterInfo(~(clusterInfo(:,3)>grandmean(1)-minXDeviation & clusterInfo(:,4)<grandmean(2)+minYDeviation), 1);
    clusterInd.TR = clusterInfo(~(clusterInfo(:,3)<grandmean(1)+minXDeviation & clusterInfo(:,4)>grandmean(2)-minYDeviation), 1);
    clusterInd.BR = clusterInfo(~(clusterInfo(:,3)<grandmean(1)+minXDeviation & clusterInfo(:,4)<grandmean(2)+minYDeviation), 1);

    %Of all the clusters, pick the right cluster for each of the 4 attribute information: 
    %Loop until there is 1 and only 1 cluster (largest size) in quadrant for the 4 AOIs

    corners = {'TL'; 'TR'; 'BL'; 'BR'};
    for j = 1:length(corners)
        if ~isempty(clusterInd.(corners{j}))
            [M,I] = max(clusterInfo(clusterInd.(corners{j}), 1:2));
            aoiInfo.(corners{j})(9) = M(1);
        else
            aoiInfo.(corners{j})(9) = 0;
        end
    end
    
    matchedClusterInd = [aoiInfo.TL(9), aoiInfo.TR(9), aoiInfo.BL(9), aoiInfo.BR(9)];
    
end