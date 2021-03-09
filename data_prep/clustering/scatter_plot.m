function scatter_plot(x, y, path)         
    h=figure;
    scatter(x, y);
    xlim([0 1]);
    ylim([0 1]);
    saveas(h, path);
end