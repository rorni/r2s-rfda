import pytest

from r2s_rfda.utils import *


@pytest.mark.parametrize('time, value, unit', [
    (0.5, 0.5, 'SECS'),
    (12, 12, 'SECS'),
    (59, 59, 'SECS'),
    (75, 1.25, 'MINS'),
    (120, 2.0, 'MINS'),
    (3540, 59, 'MINS'),
    (3600, 1.0, 'HOURS'),
    (7200, 2.0, 'HOURS'),
    (23*3600, 23.0, 'HOURS'),
    (24*3600, 1.0, 'DAYS'),
    (36*3600, 1.5, 'DAYS'),
    (363*24*3600, 363.0, 'DAYS'),
    (365*24*3600, 1.0, 'YEARS'),
    (2*365*24*3600, 2.0, 'YEARS')
])
def test_adjust_time(time, value, unit):
    adj_val, adj_unit = adjust_time(time)
    assert adj_unit == unit
    assert adj_val == value
