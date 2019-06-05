# -*- coding: utf-8 -*-

import pytest

from r2s_rfda import source


@pytest.mark.parametrize('bins, start_name', [
    ([1, 2, 3, 4], 1), ([1, 2, 3, 4], 2)
])
def test_create_bin_distributions(bins, start_name):
    new_name, distrs = source.create_bin_distributions(bins, start_name)
    assert len(distrs) == len(bins) - 1
    assert new_name == start_name + len(distrs)
    for i, d in enumerate(distrs):
        assert d._values == [bins[i], bins[i+1]]
        assert d._probs == [1]
        assert d.name == start_name + i

