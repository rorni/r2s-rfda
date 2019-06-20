# -*- coding: utf-8 -*-

import pytest
import numpy as np
from mckit.fmesh import RectMesh

from r2s_rfda import source
from r2s_rfda import data


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


sources = [
"""C total gamma intensity = 1.05000e+02
SDEF PAR=2 EFF=0.01 CEL=D1 ERG=FCEL D2 X=FCEL D3 Y=FCEL D4 Z=FCEL D5
SI1 L 300 300 200 300 200 300 200
SP1 D 10 15 10 15 20 20 15
DS2 S 6 6 7 7 7 7 7
DS3 S 8 9 8 8 8 9 9
DS4 S 10 10 10 10 11 10 11
DS5 S 12 12 12 12 12 12 12
SI6 H 0 1
SP6 D 0 1
SI7 H 1 20
SP7 D 0 1
SI8 H -1 1
SP8 D 0 1
SI9 H 1 3
SP9 D 0 1
SI10 H -1 2
SP10 D 0 1
SI11 H 2 4
SP11 D 0 1
SI12 H 2 5
SP12 D 0 1""",

"""C total gamma intensity = 1.05000e+02
SDEF PAR=2 EFF=0.01 CEL=D1 ERG=FCEL D2 X=FCEL D3 Y=FCEL D4 Z=FCEL D5
SI1 L 300 300 200 200 200 300 300
SP1 D 10 15 10 20 15 15 20
DS2 S 6 6 7 7 7 7 7
DS3 S 8 9 8 8 9 8 9
DS4 S 10 10 10 11 11 10 10
DS5 S 12 12 12 12 12 12 12
SI6 H 0 1
SP6 D 0 1
SI7 H 1 20
SP7 D 0 1
SI8 H -1 1
SP8 D 0 1
SI9 H 1 3
SP9 D 0 1
SI10 H -1 2
SP10 D 0 1
SI11 H 2 4
SP11 D 0 1
SI12 H 2 5
SP12 D 0 1""",

"""C total gamma intensity = 2.40000e+01
SDEF PAR=2 EFF=0.01 CEL=D1 ERG=FCEL D2 X=FCEL D3 Y=FCEL D4 Z=FCEL D5
SI1 L 300 300 200 200 200 300 300
SP1 D 2.5 3.0 2.5 5.0 3.0 3.0 5.0
DS2 S 6 6 7 7 7 7 7
DS3 S 8 9 8 8 9 8 9
DS4 S 10 10 10 11 11 10 10
DS5 S 12 12 12 12 12 12 12
SI6 H 0 1
SP6 D 0 1
SI7 H 1 20
SP7 D 0 1
SI8 H -1 1
SP8 D 0 1
SI9 H 1 3
SP9 D 0 1
SI10 H -1 2
SP10 D 0 1
SI11 H 2 4
SP11 D 0 1
SI12 H 2 5
SP12 D 0 1"""
]

@pytest.mark.parametrize('gamma_data, start_distr, src_index', [
    (data.GammaFrame(
        np.array([[0, 0, 0, 10, 15], [10, 20, 15, 15, 20]]), 
        data.SpatialIndex([
            (200, 0, 0, 0), (200, 0, 1, 0), (200, 1, 1, 0), (300, 0, 0, 0),
            (300, 1, 0, 0)
        ]), 3, [0, 1, 20], RectMesh((-1, 1, 3), (-1, 2, 4), (2, 5))
     ), 1, 1
    ),
    (data.GammaFrame(
        np.array([[0, 0, 0, 10, 15], [10, 20, 15, 15, 20]]), 
        data.SpatialIndex([
            (200, 0, 0, 0), (200, 0, 1, 0), (200, 1, 1, 0), (300, 0, 0, 0),
            (300, 1, 0, 0)
        ]), 3, [0, 1, 20], RectMesh((-1, 1, 3), (-1, 2, 4), (2, 5))
     ), 1, 1
    ),
    (data.GammaFrame(
        np.array([[0, 0, 0, 2.5, 3], [2.5, 5, 3, 3, 5]]), 
        data.SpatialIndex([
            (200, 0, 0, 0), (200, 0, 1, 0), (200, 1, 1, 0), (300, 0, 0, 0),
            (300, 1, 0, 0)
        ]), 3, [0, 1, 20], RectMesh((-1, 1, 3), (-1, 2, 4), (2, 5))
     ), 1, 2
    )   
])
def test_create_source(gamma_data, start_distr, src_index):
    answer = sources[src_index]
    sdef = source.create_source(gamma_data, start_distr=start_distr)
    print(sdef)
    assert sdef == answer

