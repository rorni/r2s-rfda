# -*- coding: utf-8 -*-

import pytest
import numpy as np

from r2s_rfda import fetch
from r2s_rfda import data


@pytest.mark.parametrize('data_dict, shape, mat_labels, answer', [
    ({(0, 10): 4, (1, 11): 3, (0, 5): 2, (3, 11): 10}, (3, 4), (5, 10, 11), 
     np.array([[2, 0, 0, 0], [4, 0, 0, 0], [0, 3, 0, 10]]))
])
def test_dict_to_array(data_dict, shape, mat_labels, answer):
    result = fetch.dict_to_array(data_dict, shape, mat_labels)
    np.testing.assert_array_equal(result, answer)


@pytest.mark.parametrize('sindex, mass_coeffs, c2m, mat_labels, answer', [
    (
        data.SpatialIndex([(1, 0, 0, 0), (2, 2, 3, 1), (2, 0, 0, 0), (1, 1, 2, 1)]),
        {(1, 0, 0, 0): 0.5, (2, 2, 3, 1): 2.0, (2, 0, 0, 0): 0.25, (1, 1, 2, 1): 3.0},
        {1: 10, 2: 20}, (10, 20),  np.array([[0.5, 3.0, 0, 0], [0, 0, 0.25, 2.0]])
    )
])
def test_flatten_mass_coeffs(sindex, mass_coeffs, c2m, mat_labels, answer):
    result = fetch.flatten_mass_coeffs(sindex, mass_coeffs, c2m, mat_labels)
    np.testing.assert_array_almost_equal(result, answer)


@pytest.mark.parametrize('sindex, flux_coeffs, answer', [
    (
        data.SpatialIndex([(1, 0, 0, 0), (2, 2, 3, 1), (2, 0, 0, 0), (1, 1, 2, 1)]),
        np.array([
            [
                [[72, 1], [2, 3], [4, 5], [6, 7]],
                [[8, 9], [10, 11], [12, 13], [14, 15]],
                [[16, 17], [18, 19], [20, 21], [22, 23]] 
            ],
            [
                [[24, 25], [26, 27], [28, 29], [30, 31]],
                [[32, 33], [34, 35], [36, 37], [38, 39]],
                [[40, 41], [42, 43], [44, 45], [46, 47]] 
            ],
            [
                [[48, 49], [50, 51], [52, 53], [54, 55]],
                [[56, 57], [58, 59], [60, 61], [62, 63]],
                [[64, 65], [66, 67], [68, 69], [70, 71]] 
            ]
        ]),
        np.array([
            [72, 13, 72, 23],
            [24, 37, 24, 47],
            [48, 61, 48, 71]
        ])
    )
])
def test_flux_coeffs(sindex, flux_coeffs, answer):
    result = fetch.flatten_flux_coeffs(sindex, flux_coeffs)
    np.testing.assert_array_equal(result, answer)


@pytest.mark.parametrize('data_dict, labels, answer', [
    (
        {10: np.array([1, 2, 3, 4]), 30: np.array([5, 6, 7, 8]), 20: np.array([9, 10, 11, 12])},
        (10, 20, 30),
        np.array([[1., 2., 3., 4.], [9., 10., 11., 12.], [5., 6., 7., 8.]])
    )
])
def test_produce_slice_array(data_dict, labels, answer):
    result = fetch.produce_slice_array(data_dict, labels)
    np.testing.assert_array_equal(result, answer)
