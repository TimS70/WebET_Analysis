function scatter_plot_clusters(x, y, z, grandmean, path)         
    h=figure;
    gscatter(x, y, z);
    xline(double(grandmean(1)));
    yline(double(grandmean(2)));
    xlim([0 1]);
    ylim([0 1]);
    saveas(h, path);
end