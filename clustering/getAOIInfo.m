function [aoiInfo] = getAOIInfo(aoiSizePercentage)
    corners = {'TL'; 'TR'; 'BL'; 'BR'};

    x_center.TL= 0.05+0.9*0.2; % Middle of left aoi, x pos
    x_center.TR= 0.05+0.9*0.8; % Middle of right aoi, x pos
    x_center.BL= 0.05+0.9*0.2; % Middle of left aoi, x pos
    x_center.BR= 0.05+0.9*0.8; % Middle of right aoi, x pos

    y_center.TL= 0.25; % Middle of top aoi, y pos
    y_center.BL= 0.75; % Middle of bottom aoi, y pos
    y_center.TR= 0.25; % Middle of top aoi, y pos
    y_center.BR= 0.75; % Middle of bottom aoi, y pos

    for k=1:length(corners)
        leftBorder   = x_center.(corners{k}) - aoiSizePercentage/2;
        rightBorder  = x_center.(corners{k}) + aoiSizePercentage/2;
        topBorder    = y_center.(corners{k}) - aoiSizePercentage/2;
        bottomBorder = y_center.(corners{k}) + aoiSizePercentage/2;
        width  = aoiSizePercentage;
        height = aoiSizePercentage;

        aoiInfo.(corners{k}) = [x_center.(corners{k}), y_center.(corners{k}), ...
            leftBorder, rightBorder, topBorder, bottomBorder, width, height];
    end
end