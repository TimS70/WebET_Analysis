add_new_aoi = function(data, aoi_width, aoi_height) {

    data$aoi = 0
    data$aoi[
        (data['x'] > ((0.05 + 0.9 * 0.2) - aoi_width / 2)) &
        (data['x'] < ((0.05 + 0.9 * 0.2) + aoi_width / 2)) &
        (data['y'] > (0.25 - aoi_height / 2)) &
        (data['y'] < (0.25 + aoi_height / 2))] = 'TL'
    
    data$aoi[
        (data['x'] > ((0.05 + 0.9 * 0.8) - aoi_width / 2)) &
        (data['x'] < ((0.05 + 0.9 * 0.8) + aoi_width / 2)) &
        (data['y'] > (0.25 - aoi_height / 2)) &
        (data['y'] < (0.25 + aoi_height / 2))] = 'TR'
    
    data$aoi[
        (data['x'] > ((0.05 + 0.9 * 0.2) - aoi_width / 2)) &
        (data['x'] < ((0.05 + 0.9 * 0.2) + aoi_width / 2)) &
        (data['y'] > (0.75 - aoi_height / 2)) &
        (data['y'] < (0.75 + aoi_height / 2))] = 'BL'
            
    data$aoi[
        (data['x'] > ((0.05 + 0.9 * 0.8) - aoi_width / 2)) &
        (data['x'] < ((0.05 + 0.9 * 0.8) + aoi_width / 2)) &
        (data['y'] > (0.75 - aoi_height / 2)) &
        (data['y'] < (0.75 + aoi_height / 2))] = 'BR'
    return(data)
}