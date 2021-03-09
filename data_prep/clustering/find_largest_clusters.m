function [largest_clusters] = find_largest_clusters(...
    cluster_aoi_info, grandmean, tolerance)  
   
    % Assign clusters to each quadrant of the screen relative to the 
    % grandmean as center.
    
    
    % tolerance: Clusters should have some distance from the center 
    % to avoid the fixation cluster.
    
    % col 1: cluster number
    % col 2: number of data points in each cluster (accumarray),
    % col 3: mean cluster x position
    % col 4: mean cluster y position
    % col 5: left border
    % col 6: Right border
    % col 7: top border
    % col 8: bottom borter
    
    % col 9: corner (TL, TR, BL, BR)
    cluster_aoi_info(:, 9) = 0;
    
    % TL: Right border (col 6) is left of x_mean 
    % and bottom border (col 8) is top of y_mean
    cluster_aoi_info((...
        cluster_aoi_info(:, 6)<grandmean(1)+tolerance & ...
        cluster_aoi_info(:, 7)>grandmean(2)-tolerance), 9) = 1;
    
    % TR: Left border (col 5) is right of x_mean 
    % and bottom border (col 8) is top of y_mean
    cluster_aoi_info((...
        cluster_aoi_info(:, 5)>grandmean(1)-tolerance & ...
        cluster_aoi_info(:, 7)>grandmean(2)-tolerance), 9) = 2;
    % BL: Right border (col 6) is left of x_mean 
    % and top border (col 7) is below y_mean
    cluster_aoi_info((...
        cluster_aoi_info(:, 6)<grandmean(1)+tolerance & ...
        cluster_aoi_info(:, 8)<grandmean(2)+tolerance), 9) = 3;
    % BR: Left border (col 5) is right of x_mean 
    % and top border (col 7) is below y_mean
    cluster_aoi_info((...
        cluster_aoi_info(:, 5)>grandmean(1)-tolerance & ...
        cluster_aoi_info(:, 7)<grandmean(2)+tolerance), 9) = 4;
    
    % Of all the clusters, pick the right cluster for each of the 4 
    % attribute information: 
    % Loop until there is 1 and only 1 cluster (largest size) in quadrant 
    % for the 4 AOIs
    
    largest_clusters = zeros(4, 9);
    
    for i = 1:4
        cluster_candidates = cluster_aoi_info(cluster_aoi_info(:, 9)==i, :);
        if  ~isempty(cluster_candidates);
            [M,I] = max(cluster_candidates(:, 2));
            largest_clusters(i, :) = cluster_candidates(I, :);
        end
    end
end