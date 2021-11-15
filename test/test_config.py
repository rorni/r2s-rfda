# -*- coding: utf-8 -*-

import pytest
from pathlib import Path
import shutil

import numpy as np

from r2s_rfda import launcher, prepare


root = Path(__file__).resolve().parent


@pytest.mark.parametrize('folder, config', [
    ('test1', {
        'approach': 'full', 'task_list': [('folder1', ['task1', 'task2']), 
        ('folder2', ['task1', 'task2', 'task3'])], 'cells': [1, 3, 4, 5, 8],
        'materials': [2, 100, 400]
    })
])
def test_config(folder, config):
    path = root / folder
    path.mkdir()

    launcher.save_config(path, **config)

    load_conf = launcher.load_config(path)
    assert load_conf == config
    shutil.rmtree(path)


@pytest.mark.parametrize('filename, result', [
    ('test/r2s_sample.ini', {
        'model': {
            'mcnp': 'input.i', 'fmesh': 'fmesh.m', 'tally': '4',   
            'transform': '0 0 0 150 120 90 60 150 90 90 90 0',
            'approach': 'simple', 'minvol': '0.001'
        }, 
        'data': {
            'ind_nuc':  r'D:\\nuclear_data\\EAF2010data\\eaf2010_decay12_index',
            'xs_endf':  r'D:\\nuclear_data\\EAF2010data\\eaf2010-n\\gxs-709',
            'xs_endfb': r'D:\\nuclear_data\\EAF2010data\\eaf2010-n\\eaf2010-n.bin',
            'prob_tab': r'D:\\nuclear_data\\EAF2010data\\eaf2010-n\\tp294',
            'fy_endf':  r'D:\\nuclear_data\\GEFY42data\\gef42_nfy',
            'sf_endf':  r'D:\\nuclear_data\\GEFY42data\\gef42_sfy',
            'dk_endf':  r'D:\\nuclear_data\\decay\\decay_2012',
            'hazards':  r'D:\\nuclear_data\\decay\\hazards_2012',
            'clear':    r'D:\\nuclear_data\\decay\\clear_2012',
            'a2data':   r'D:\\nuclear_data\\decay\\a2_2012',
            'absorp':   r'D:\\nuclear_data\\decay\\abs_2012'
        },
        'fispact': {
            'inventory': 'inventory.temp',
            'libxs':     '1',
            'norm_flux': '4.5643E+12'
        }
    })
])
def test_load_task(filename, result):
    model_conf, data_conf, fispact_conf = launcher.load_task(filename)
    assert len(model_conf) == len(result['model'])
    assert len(data_conf) == len(result['data'])
    assert len(fispact_conf) == len(result['fispact'])
    for k, v in result['model'].items():
        assert v == model_conf[k]
    for k, v in result['data'].items():
        assert v == data_conf[k]
    for k, v in result['fispact'].items():
        assert v == fispact_conf[k]


@pytest.mark.parametrize('input, translation, rotation, indegrees', [
    (
        '0 0 0 150 120 90 60 150 90 90 90 0', [0, 0, 0], 
        [150, 120, 90, 60, 150, 90, 90, 90, 0], False
    ),
    (
        '*(0 0 0 150 120 90 60 150 90 90 90 0)', [0, 0, 0], 
        [150, 120, 90, 60, 150, 90, 90, 90, 0], True
    ),
    (
        '0 0 0', [0, 0, 0], 
        None, False
    ),
])
def test_parse_transformation(input, translation, rotation, indegrees):
    trans, rot, deg = prepare.parse_transforamtion(input)
    np.testing.assert_allclose(trans, translation)
    if rotation is None:
        assert rot is None
    else:
        np.testing.assert_allclose(rot, rotation)
    assert indegrees == deg
