def is_float(x):
    try:
        return float(x) == int(x)
    except:
        return False


def is_int(x):
    try:
        int(x)
        return True
    except:
        return False