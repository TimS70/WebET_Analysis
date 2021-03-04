function [cluster_aoi_info] = get_cluster_aoi_info(...
    data, clusters, nClusters, aoi_width ,aoi_height)
    %Summarize info about clusters 
    % col 1: cluster number
    % col 2: number of data points in each cluster (accumarray),
    % col 3: mean cluster x position
    % col 4: mean cluster y position
    % col 5: left border
    % col 6: right border
    % col 7: top border
    % col 8: bottom borter
    means=grpstats(data, clusters);
    cluster_aoi_info=[(1:nClusters)',accumarray(clusters,1),means(:,3:4)];
    cluster_aoi_info(:, 5) = cluster_aoi_info(:, 3) - aoi_width/2;
    cluster_aoi_info(:, 6) = cluster_aoi_info(:, 3) + aoi_width/2;
    cluster_aoi_info(:, 7) = cluster_aoi_info(:, 4) - aoi_height/2;
    cluster_aoi_info(:, 8) = cluster_aoi_info(:, 4) + aoi_height/2;   
end