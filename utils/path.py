import os


def makedir(*args):
    path = os.path.join(*args)
    os.makedirs(path, exist_ok=True)

    return path
