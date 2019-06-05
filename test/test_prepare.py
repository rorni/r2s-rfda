# -*- coding: utf-8 -*-

import pytest
from mckit import Composition

from r2s_rfda import prepare


@pytest.mark.parametrize('material, mass, density, answer', [
    (Composition(atomic=[('H', 2), ('O', 1)]), 2.e+3, 1.0, 
     'DENSITY 1.0000e+00\nFUEL 5\n  H1 1.3370e+26\n  H2 1.5377e+22\n  O16 6.6693e+25\n  O17 2.5405e+22\n  O18 1.3705e+23'),
    (Composition(atomic=[('H', 2), ('O', 1)]), 2.e+3, 2.0, 
     'DENSITY 2.0000e+00\nFUEL 5\n  H1 1.3370e+26\n  H2 1.5377e+22\n  O16 6.6693e+25\n  O17 2.5405e+22\n  O18 1.3705e+23'),
])
def test_material_description(material, mass, density, answer):
    result = prepare.material_description(material, mass, density)
    assert result == answer
