# -*- coding: utf-8 -*-

_TIME_UNITS = {'s': 1, 'm': 60, 'h': 3600, 'd': 24 * 3600, 'y': 24 * 3600 * 365}


def convert_time_literal(timelit):
    """Converts time literal string to int.

    Parameters
    ----------
    timelit : str
        Time literal string. If it is just a number, then it is given in sec.
        If it is the number immediately followed by one of the literals like
        's' - for sec, 'd' - for days, 'm' - for minutes, 'h' - for hours, 
        'y' - for years.
    
    Returns
    -------
    timeval : int
        Time value in seconds.
    """
    if timelit[-1].isalpha():
        unit = timelit[-1].lower()
        value = timelit[:-1]
    else:
        value = timelit
        unit = 's'
    mult = _TIME_UNITS[unit]
    if len(value) == 0:
        value = '1'
    timeval = float(value) * mult
    return int(timeval)
    