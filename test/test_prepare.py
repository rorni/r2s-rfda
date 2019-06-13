# -*- coding: utf-8 -*-

import pytest
from mckit import Composition, read_mcnp
from mckit.fmesh import RectMesh

from r2s_rfda import prepare


materials = [
    'DENSITY 1.0000e+00\nFUEL 5\n  H1 1.3370e+26\n  H2 1.5377e+22\n  O16 6.6693e+25\n  O17 2.5405e+22\n  O18 1.3705e+23',
    'DENSITY 2.0000e+00\nFUEL 5\n  H1 1.3370e+26\n  H2 1.5377e+22\n  O16 6.6693e+25\n  O17 2.5405e+22\n  O18 1.3705e+23'
]

@pytest.mark.parametrize('material, mass, density, mat_index', [
    (Composition(atomic=[('H', 2), ('O', 1)]), 2.e+3, 1.0, 0),
    (Composition(atomic=[('H', 2), ('O', 1)]), 2.e+3, 2.0, 1),
])
def test_material_description(material, mass, density, mat_index):
    answer = materials[mat_index]
    result = prepare.material_description(material, mass, density)
    assert result == answer


@pytest.fixture
def mesh():
    return RectMesh([2, 4, 6, 8, 10], [1, 3, 5], [0, 3])


@pytest.fixture
def model():
    return read_mcnp('test/prepare/model1.i')


@pytest.mark.parametrize('cell_names', [
    [1, 2, 10, 21]
])
def test_select_cells(model, mesh, cell_names):
    cells = prepare.select_cells(model, mesh.bounding_box())
    assert set(cell_names) == set(c.name() for c in cells)


@pytest.mark.parametrize('answer', [
    {
        (1, 0, 1, 0): 3, (1, 1, 1, 0): 6, (1, 2, 1, 0): 3, (2, 1, 0, 0): 3,
        (2, 1, 1, 0): 3, (2, 2, 0, 0): 3, (2, 2, 1, 0): 3, (10, 0, 0, 0): 3,
        (10, 1, 0, 0): 1.5, (10, 0, 1, 0): 3, (10, 1, 1, 0): 1.5,
        (21, 2, 0, 0): 1.047, (21, 2, 1, 0): 1.047, (21, 3, 0, 0): 1.047, 
        (21, 3, 1, 0): 1.047
    }
])
def test_calculate_volumes(model, mesh, answer):
    cells = prepare.select_cells(model, mesh.bounding_box())
    for c in cells:
        print(c.mcnp_repr())
    volumes = prepare.calculate_volumes(cells, mesh, min_volume=1.e-6)
    print(volumes)
    assert len(answer) == len(volumes)
    for k, v in volumes.items():
        print(k)
        assert v == pytest.approx(answer[k], 0.02)
