# -*- coding: utf-8 -*-

import numpy as np
import mckit.source as mcs

from . import data


def create_source(gamma_data, vol_dict, start_distr=1, int_filter=1.e-9, vol_filter=1.e-3):
    """Creates MCNP SDEF for gamma source.

    Parameters
    ----------
    gamma_data : SparseData
        Data on gamma yield for every cell and voxel.
    start_distr : int
        Starting SDEF distribution number.
    
    Returns
    -------
    sdef : str
        MCNP SDEF description.
    """
    source, intensity = activation_gamma_source(
        gamma_data, vol_dict, start_distr, int_filter=int_filter, vol_filter=vol_filter
    )
    sdef = 'C total gamma intensity = {0:.5e}\n{1}'.format(intensity, source.mcnp_repr())
    return sdef


def activation_gamma_source(gamma_data, vol_dict, start_name=1, int_filter=1.e-9, vol_filter=1.e-3):
    """Creates activation gamma source.

    Parameters
    ----------
    gamma_data : SparseData
        Gamma source intensity data.
    start_name : int
        Starting name for distributions. Default: 1.

    Returns
    -------
    source : mckit.Source
        MCNP gamma source.
    total_intensity : float
        Total gamma source intensity.
    """
    aux_name = start_name + 5
    xbins = gamma_data.xbins
    ybins = gamma_data.ybins
    zbins = gamma_data.zbins
    # energy
    aux_name, e_distr = create_bin_distributions(gamma_data.gbins, aux_name)
    # xbins
    aux_name, x_distr = create_bin_distributions(xbins, aux_name)
    # ybins
    aux_name, y_distr = create_bin_distributions(ybins, aux_name)
    # zbins
    aux_name, z_distr = create_bin_distributions(zbins, aux_name)
    
    probs = []
    e_indices = []
    x_indices = []
    y_indices = []
    z_indices = []
    c_values = []
    
    indices = []
    intensities = []
    for index, intensity in gamma_data.iter_nonzero():
        indices.append(index)
        intensities.append(intensity)
    total_intensity = sum(intensities)
    
    for (g, c, i, j, k), intensity in zip(indices, intensities):
        if intensity / total_intensity < int_filter:
            continue
        voxel_vol = (xbins[i+1] - xbins[i]) * (ybins[j+1] - ybins[j]) * (zbins[k+1] - zbins[k])
        if vol_dict[c, i, j, k] / voxel_vol < vol_filter:
            continue
        probs.append(intensity)
        e_indices.append(e_distr[g])
        c_values.append(c)
        x_indices.append(x_distr[i])
        y_indices.append(y_distr[j])
        z_indices.append(z_distr[k])    

    cell_dist = mcs.Distribution(start_name, c_values, probs, 'CEL')
    e_dist = mcs.Distribution(start_name + 1, e_indices, cell_dist, 'ERG')
    x_dist = mcs.Distribution(start_name + 2, x_indices, cell_dist, 'X')
    y_dist = mcs.Distribution(start_name + 3, y_indices, cell_dist, 'Y')
    z_dist = mcs.Distribution(start_name + 4, z_indices, cell_dist, 'Z')

    src_params = {
        'PAR': 2, 'EFF': 1.e-3, 'CEL': cell_dist, 'ERG': e_dist, 
        'X': x_dist, 'Y': y_dist, 'Z': z_dist
    }
    return mcs.Source(**src_params), total_intensity


def create_bin_distributions(bins, start_name):
    """Creates individual distributions for every bin.

    Parameters
    ----------
    bins : array_like 
        Bin boundaries.
    start_name : int
        Starting name of the distributions.

    Returns
    -------
    free_name : int
        Distribution name, that can be used for new distributions.
    distributions : list
        A list of created distributions.
    """
    distributions = []
    for i in range(len(bins) - 1):
        distributions.append(
            mcs.Distribution(start_name, bins[i:i+2], [1])
        )
        start_name += 1
    return start_name, distributions

