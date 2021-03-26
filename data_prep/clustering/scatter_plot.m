function scatter_plot(x, y, path, file_name)    
    h=figure;
    scatter(x, y);
    xlim([0 1]);
    ylim([0 1]);
    save_file(h, path, file_name)
end