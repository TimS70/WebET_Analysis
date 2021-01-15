function [dataWithClusters, aoiInfo, clusterInfo, matchedClusterInd] = getClusters(data, grandmean, aoiSizePercentage, screen_width, screen_height) 
    % maximum cluster to extract, can edit
    nClusters = 20;
    
    aoiInfo = getAOIInfo(screen_width, screen_height, aoiSizePercentage);
    clusters=clusterdata(data(:, 3:4),'linkage','centroid','savememory','on','maxclust',nClusters);
    dataWithClusters=[data clusters];    
    clusterInfo = assembleClusterInfo(dataWithClusters, clusters, nClusters, screen_width, screen_height, aoiSizePercentage);
    % col 9: largest cluster
    [aoiInfo, matchedClusterInd] = matchClustersWithAOI(aoiInfo, clusterInfo, grandmean, screen_width, screen_height); 

end