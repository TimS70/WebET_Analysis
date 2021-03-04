function savePlot(x, y, xMax, yMax, path, index)         
    h=figure
    scatter(x, y)
    xlim([0 xMax])
    ylim([0 yMax])
    saveas(h,sprintf(path, index));
end