def transform_xy_coordinates(data_et):

    data_et = data_et.copy()

    print(f"""Gaze points as percentage of screen size -- Pixel: \n"""
          f"""{data_et[['x', 'y']].describe()} \n""")

    # screen which was 1280 X 1024 pixels.
    data_et['x'] = data_et['x'] / 1280
    data_et['y'] = data_et['y'] / 1024

    print(f"""Percentage: \n"""
          f"""{data_et[['x', 'y']].describe()} \n""")

    return data_et
