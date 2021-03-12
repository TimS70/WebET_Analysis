def clean_corr_data(data_plot):
    print('Cleaning data for correlation analysis...')
    null_data = data_plot.loc[data_plot.isnull().any(axis=1), :]

    if len(null_data) > 0:
        print('! Attention ! Missing values')
        print(
            f"""Length of data raw: {len(data_plot)} \n""")
    else:
        print('No missing data found')

    data_plot_clean = data_plot.loc[~data_plot.isnull().any(axis=1), :]

    print(f"""Length of data clean: {len(data_plot_clean)} \n""")

    return data_plot_clean
