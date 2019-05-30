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
def test_create_scenario_template(input, norm_flux, templ, coeffs):
    input = load_file(input)
    templ = load_file(templ)
    template.create_scenario_template(input, norm_flux)
    assert template.inventory_temp == templ
    np.testing.assert_array_almost_equal(template.flux_coeffs, coeffs)


@pytest.mark.parametrize('datalib, answer', [
    ('ind_nuc  ../../TENDL2014data/tendl14_decay12_index\nxs_endf  ../../TENDL2014data/tal2014-n/gxs-709',
     'files_1')
])
def test_fispact_files(datalib, answer):
    answer = load_file(answer)
    result = template.fispact_files(datalib)
    assert result == answer


@pytest.mark.parametrize('libxs, nestrc, answer', [
    (1, 175, 'collapse_1.i'), 
    (-1, 175, 'collapse_2.i')
])
def test_fispact_collapse(libxs, nestrc, answer):
    answer = load_file(answer)
    result = template.fispact_collapse(libxs, nestrc)
    assert result == answer


@pytest.mark.parametrize('flux, material, answer', [

])
def test_fispact_inventory(flux, material, answer):
    result = template.fispact_inventory(flux, material)
    assert result == answer


@pytest.mark.parametrize('ebins, flux, answer', [

])
def test_fispact_arbflux(ebins, flux, answer):
    result = template.create_arbflux_text(ebins, flux)
    assert result == answer
