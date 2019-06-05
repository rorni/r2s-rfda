# -*- coding: utf-8 -*-

import pytest

from r2s_rfda import utils


@pytest.mark.parametrize('timelit, answer', [
    ('1', 1), ('2', 2), ('209', 209), ('30s', 30), ('45S', 45), ('s', 1),
    ('h', 3600), ('1h', 3600), ('3h', 3600*3), ('10h', 36000), ('m', 60),
    ('21m', 21 * 60), ('d', 24 * 3600), ('3d', 3 * 24 * 3600), 
    ('y', 365 * 24 * 3600), ('5y', 365 * 24 * 3600 * 5), ('1.5h', 5400)
])
def test_convert_time_literal(timelit, answer):
    result = utils.convert_time_literal(timelit)
    assert result == answer
    assert isinstance(result, int)
