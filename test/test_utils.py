# -*- coding: utf-8 -*-

import pytest
from pkg_resources import resource_filename

from r2s_rfda import utils


@pytest.mark.parametrize('timelit, answer', [
    ('1', 1), ('2', 2), ('209', 209), ('30s', 30), ('45S', 45), ('s', 1),
    ('h', 3600), ('1h', 3600), ('3h', 3600*3), ('10h', 36000), ('m', 60),
    ('21m', 21 * 60), ('d', 24 * 3600), ('3d', 3 * 24 * 3600), 
    ('y', 365.25 * 24 * 3600), ('5y', 365.25 * 24 * 3600 * 5), ('1.5h', 5400)
])
def test_convert_time_literal(timelit, answer):
    result = utils.convert_time_literal(timelit)
    assert result == answer
    assert isinstance(result, int)


def load_file(filename):
    with open(resource_filename(__name__, 'templates/' + filename)) as f:
        template = f.read()
    return template


@pytest.mark.parametrize('filename, answer', [
    ('input_0.i', 37),
    ('input_1.i', 43),
    ('input_2.i', 139),
    ('input_3.i', 139),
    ('input_4.i', None)
])
def test_find_zero_step(filename, answer):
    text = load_file(filename)
    result = utils.find_zero_step(text)
    assert result == answer


@pytest.mark.parametrize('t, time_labels, answer', [
    (349, [0, 5, 349, 350, 400], 349),
    (0, [0, 4, 5, 6, 7], 0),
    (0, [1, 2, 3, 4, 5], 1),
    (349, [0, 5, 340, 350, 400], 350),
    (349, [0, 5, 340, 360, 400], 340)
])
def test_find_closest(t, time_labels, answer):
    result = utils.find_closest(t, time_labels)
    assert result == answer
