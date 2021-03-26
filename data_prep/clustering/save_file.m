function save_file(object, path, file_name)    

    if ~exist(path)
        mkdir(path)
    end
    
    saveas(object, fullfile(path, file_name));
end