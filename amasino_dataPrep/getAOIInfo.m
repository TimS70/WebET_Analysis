function [aoiInfo] = getAOIInfo(screen_width, screen_height, aoiSizePercentage)
    corners = {'TL'; 'TR'; 'BL'; 'BR'};

    x_center.TL= ((0.05+0.9*0.2) * screen_width); % Middle of left aoi, x pos
    x_center.TR= ((0.05+0.9*0.8) * screen_width); % Middle of right aoi, x pos
    x_center.BL= ((0.05+0.9*0.2) * screen_width); % Middle of left aoi, x pos
    x_center.BR= ((0.05+0.9*0.8) * screen_width); % Middle of right aoi, x pos

    y_center.TL= (0.25 * screen_height); % Middle of top aoi, y pos
    y_center.BL= (0.75 * screen_height); % Middle of bottom aoi, y pos
    y_center.TR= (0.25 * screen_height); % Middle of top aoi, y pos
    y_center.BR= (0.75 * screen_height); % Middle of bottom aoi, y pos

    for k=1:length(corners)
        leftBorder   = (x_center.(corners{k}) - (aoiSizePercentage/2) * screen_width);
        rightBorder  = (x_center.(corners{k}) + (aoiSizePercentage/2) * screen_width);
        topBorder    = (y_center.(corners{k}) - (aoiSizePercentage/2) * screen_height);
        bottomBorder = (y_center.(corners{k}) + (aoiSizePercentage/2) * screen_height);
        width  = screen_width * aoiSizePercentage;
        height = screen_height * aoiSizePercentage;

        aoiInfo.(corners{k}) = [x_center.(corners{k}), y_center.(corners{k}), ...
            leftBorder, rightBorder, topBorder, bottomBorder, width, height];
    end
end