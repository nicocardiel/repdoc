def str_nonan(s):
    """Avoid NaN due to empty strings: return single space instead.

    """

    if len(s) > 0:
        return s
    else:
        return ' '
