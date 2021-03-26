function scatter_plot_clusters(x, y, z, grandmean, path, file_name)

    h=figure;
    gscatter(x, y, z);
    xline(double(grandmean(1)));
    yline(double(grandmean(2)));
    xlim([0 1]);
    ylim([0 1]);
    save_file(h, path, file_name)
end