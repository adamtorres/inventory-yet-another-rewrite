def minimal_number(x):
    """
    Returns decimals only if the number has non-zero decimals.  Returns an int if none.
    :param x: some number.  Defaults to 0 if empty string.
    :return: int if no decimal value or float if non-zero decimal value.
    """
    if type(x) is str:
        if x == '':
            x = 0
    f = float(x)
    if f.is_integer():
        return int(f)
    else:
        return f
