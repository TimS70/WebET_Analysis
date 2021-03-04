function [dataWithClusters, aoiInfo, clusterInfo, matchedClusterInd] = getClusters(data, grandmean, aoiSizePercentage) 
    % maximum cluster to extract, can edit
    nClusters = 20;
    
    aoiInfo = getAOIInfo(aoiSizePercentage);
    clusters=clusterdata(data(:, 3:4),'linkage','centroid','savememory','on','maxclust',nClusters);
    dataWithClusters=[data clusters];    
    clusterInfo = assembleClusterInfo(dataWithClusters, clusters, nClusters, aoiSizePercentage);
    % col 9: largest cluster
    [aoiInfo, matchedClusterInd] = matchClustersWithAOI(aoiInfo, clusterInfo, grandmean); 

end