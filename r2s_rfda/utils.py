# -*- coding: utf-8 -*-

import re
from collections import deque


_TIME_UNITS = {'s': 1, 'm': 60, 'h': 3600, 'd': 24 * 3600, 'y': 24 * 3600 * 365.25}


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


def find_zero_step(text):
    """Finds index of last irradiation step.

    Parameters
    ----------
    text : str
        Text of fispact inventory file.

    Returns
    -------
    zero : int
        Index of last moment of irradiation, after which time is reset.
    """
    halfs = re.split('ZERO', text, flags=re.MULTILINE+re.IGNORECASE)
    if len(halfs) == 2:
        pulses = deque(re.split('(PULSE +\\d+|ENDPULSE)', halfs[0]))
        return count_group(pulses) - 1
    else:
        return None

    
def count_group(groups):
    count = 0
    while len(groups) > 0:
        group = groups.popleft()
        if group.startswith('PULSE'):
            repeats = int(group.split()[1])
            count += count_group(groups) * repeats
        elif group == 'ENDPULSE':
            return count
        else:
            count_s = group.count('SPEC')
            count_a = group.count('ATOMS')
            count += count_s + count_a
    return count