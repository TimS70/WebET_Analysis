function [clusterInfo] = assembleClusterInfo(data, clusters, nClusters, screen_width, screen_height, aoiSizePercentage)
    %Summarize info about clusters 
    % col 1: cluster number
    % col 2: number of data points in each cluster (accumarray),
    % col 3: mean cluster x position
    % col 4: mean cluster y position
    % col 5: left border
    % col 6: right border
    % col 7: top border
    % col 8: bottom borter
    means=grpstats(data,clusters);
    clusterInfo=[(1:nClusters)',accumarray(clusters,1),means(:,3:4)];
    clusterInfo(:, 5) = clusterInfo(:, 3) - (aoiSizePercentage/2) * screen_width;
    clusterInfo(:, 6) = clusterInfo(:, 3) + (aoiSizePercentage/2) * screen_width;
    clusterInfo(:, 7) = clusterInfo(:, 4) - (aoiSizePercentage/2) * screen_height;
    clusterInfo(:, 8) = clusterInfo(:, 4) + (aoiSizePercentage/2) * screen_height;   
end