# -*- coding: utf-8 -*-

import pytest
from mckit import Composition
from mckit.fmesh import RectMesh

from r2s_rfda import prepare
from r2s_rfda.prepare import read_mcnp


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


@pytest.fixture
def cells(model, mesh):
    return prepare.select_cells(model, mesh.bounding_box())


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
def test_calculate_volumes(cells, mesh, answer):
    volumes = prepare.calculate_volumes(cells, mesh, min_volume=1.e-6)
    assert len(answer) == len(volumes)
    for k, v in volumes.items():
        assert v == pytest.approx(answer[k], 0.02)


@pytest.mark.parametrize('answer', [
    {1: 1, 2: 2, 10: 2, 21: 1}
])
def test_get_materials(cells, answer):
    mats = prepare.get_materials(cells)
    assert {k: m.name() for k, m in mats.items()} == answer


@pytest.mark.parametrize('answer', [
    {1: 7.8, 2: 1, 10: 1, 21: 7.8}
])
def test_get_density(cells, answer):
    dens = prepare.get_densities(cells)
    assert answer == pytest.approx(dens, 1.e-3)


@pytest.mark.parametrize('vol_dict, den_dict, answer', [
    (
        {(1, 1, 2, 3): 0.5, (1, 3, 4, 0): 2.5, (3, 0, 1, 2): 1.0, (3, 1, 2, 3): 1.5},
        {1: 2.0, 3: 4.0}, 
        {(1, 1, 2, 3): 1, (1, 3, 4, 0): 5, (3, 0, 1, 2): 4, (3, 1, 2, 3): 6}
    )
])
def test_get_masses(vol_dict, den_dict, answer):
    masses = prepare.get_masses(vol_dict, den_dict)
    assert answer == pytest.approx(masses, 1.e-3)


# @pytest.mark.skip
# @pytest.mark.parametrize('clabs, mlabs, matdict, answer', [
#     (
#         (1, 3, 4, 5), (101, 102), {
#             1: Composition(atomic=[('Al', 1)], name=101),
#             3: Composition(atomic=[('Fe', 1)], name=102),
#             4: Composition(atomic=[('Al', 1)], name=101),
#             5: Composition(atomic=[('Fe', 1)], name=102)
#         },
#         (
#             ('cell', 'material'), ((1, 3, 4, 5), (101, 102)),
#             {(0, 0): 1, (1, 1): 1, (2, 0): 1, (3, 1): 1}
#         )
#     )
# ])
# def test_cm_matrix(clabs, mlabs, matdict, answer):
#     result = prepare.cm_matrix(clabs, mlabs, matdict)
#     assert result.axes == answer[0]
#     assert result.labels == answer[1]
#     assert result.data.nnz == len(answer[2])
#     for index, value in answer[2].items():
#         assert value == result.data[index]
