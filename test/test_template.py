# -*- coding: utf-8 -*-

import pytest
import numpy as np
from pkg_resources import resource_filename

from r2s_rfda import template


def load_file(filename):
    with open(resource_filename(__name__, 'templates/' + filename)) as f:
        template = f.read()
    return template


@pytest.mark.parametrize('input, norm_flux, templ, coeffs', [
    ('input_1.i', 4.5643E+12, 'temp_1.i', [0.00535723, 0.04125058, 0.08303573, 1., 1.39999562])
])
def test_init_inventory_template(input, norm_flux, templ, coeffs):
    input = load_file(input)
    templ = load_file(templ)
    template.init_inventory_template(input, norm_flux)
    assert template.inventory_temp == templ
    np.testing.assert_array_almost_equal(template.flux_coeffs, coeffs)


@pytest.mark.parametrize('datalib, answer', [
    ({'ind_nuc': '../../TENDL2014data/tendl14_decay12_index',
      'xs_endf': '../../TENDL2014data/tal2014-n/gxs-709',
      'clear': '../../decay/clear_2012'}, 'files_1')
])
def test_fispact_files(datalib, answer):
    answer = load_file(answer)
    template.init_files_template(datalib)
    result = template.fispact_files()
    assert result == answer


@pytest.mark.parametrize('libxs, nestrc, answer', [
    (1, 175, 'collapse_1.i'), 
    (-1, 175, 'collapse_2.i')
])
def test_fispact_collapse(libxs, nestrc, answer):
    answer = load_file(answer)
    template.init_collapse_template(libxs, nestrc)
    result = template.fispact_collapse()
    assert result == answer


@pytest.fixture
def temp():
    inp = load_file('input_0.i')
    template.init_inventory_template(inp, 1.0e+10)


@pytest.mark.parametrize('flux, material, answer', [
    (1.0e+10, 'DENSITY 2.0\nFUEL 2\n  Li6  8.5E+24\n  Li7  1.5E+24', 'temp_01.i'),
    (2.0e+10, 'DENSITY 3.5\nFUEL 2\n  Fe56  7.5E+24\n  Co60  3.5E+24', 'temp_02.i'),
    (1.0e+11, 'DENSITY 7.8\nMASS 1.0 7\n  Fe 65.255\n  Cr 18.0\n  Ni 12.015\n'
        '  Mo 2.4\n  Mn 1.8\n  Si 0.5\n  C  0.03', 'temp_03.i'),
    (1.0e+09, 'MASS 6.0 5\n  Fe 65.255\n  Cr 18.0\n  Ni 12.015\n  Mo 2.4\n  Mn 1.8', 'temp_04.i')
])
def test_fispact_inventory(temp, flux, material, answer):
    result = template.fispact_inventory(flux, material)
    assert result == answer


@pytest.mark.parametrize('ebins, flux, answer', [
    ([1.e-11, 1.0, 10.0], [1, 90], 'arb_flux_1'),
    ([1.1e-11, 2.5e-7, 1.4e-3, 2.46e-1, 3.8, 4.6, 7.8, 14.1], 
     [3.6e+5, 2.3e+2, 6.7e+8, 1.2e+6, 7.8e+7, 9.4e+9, 2.87e+3], 'arb_flux_2')
])
def test_fispact_arbflux(ebins, flux, answer):
    answer = load_file(answer)
    result = template.create_arbflux_text(ebins, flux)
    print(result)
    print('----')
    print(answer)
    assert result == answer
