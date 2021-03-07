from utils.path import makedir


def add_et_variables(data_et):
    data_et = invert_y_axis(data_et)

    return data_et


def invert_y_axis(data_et):
    data_et['y'] = 1 - data_et['y']
    print(
        f"""data_et: Inverted y-axis: \n """
        f"""{data_et['y'].describe()} \n""")

    return data_et