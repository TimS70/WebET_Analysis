function [aoi_info] = get_aoi_info(aoi_width, aoi_height)
    
    corners = {'TL'; 'TR'; 'BL'; 'BR'};

    x_center.TL= 0.05+0.9*0.2; % Middle of left aoi, x pos
    x_center.TR= 0.05+0.9*0.8; % Middle of right aoi, x pos
    x_center.BL= 0.05+0.9*0.2; % Middle of left aoi, x pos
    x_center.BR= 0.05+0.9*0.8; % Middle of right aoi, x pos

    y_center.TL= 0.75; % Middle of top aoi, y pos
    y_center.TR= 0.75; % Middle of top aoi, y pos
    y_center.BL= 0.25; % Middle of bottom aoi, y pos
    y_center.BR= 0.25; % Middle of bottom aoi, y pos

    aoi_info = zeros(4, 9);
    for i=1:4
        leftBorder   = x_center.(corners{i}) - aoi_width/2;
        rightBorder  = x_center.(corners{i}) + aoi_width/2;
        topBorder    = y_center.(corners{i}) + aoi_height/2;
        bottomBorder = y_center.(corners{i}) - aoi_height/2;
        width  = aoi_width;
        height = aoi_height;

        aoi_info(i, :) = [...
            x_center.(corners{i}), y_center.(corners{i}), ...
            leftBorder, rightBorder, bottomBorder, topBorder, ...
            width, height, i];
    end
end