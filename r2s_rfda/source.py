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


def activation_gamma_source(gamma_data, vol_dict, start_name=1, int_filter=1.e-9, vol_filter=1.e-3, white_list=None):
    """Creates activation gamma source.

    Parameters
    ----------
    gamma_data : SparseData
        Gamma source intensity data.
    vol_dict : dict
        A dictionary of cell volumes.
    start_name : int
        Starting name for distributions. Default: 1.
    int_filter : float
        Intensity filter. Relative treshold, below which source bins will be
        rejected. Default: 1.e-9
    vol_filter : float
        Volume filter. Cell parts with volume less than this fraction of voxel
        volume will be removed from source distribution.
    white_list : list
        List of cells constituting the gamma source.

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

    voxel_vols = get_mesh_volumes(xbins, ybins, zbins)    
    
    probs = []
    e_indices = []
    x_indices = []
    y_indices = []
    z_indices = []
    c_values = []
    
    indices = []
    intensities = []
    if white_list is None:
        for index, intensity in gamma_data.iter_nonzero():
            indices.append(index)
            intensities.append(intensity)
    else:
        for index, intensity in gamma_data.iter_nonzero():
            if index[1] in white_list:
                indices.append(index)
                intensities.append(intensity)
    total_intensity = sum(intensities)
    print('Total gamma intensity: {0:.4e} g/sec'.format(total_intensity))

    int_rejected = 0
    vol_rejected = 0

    for (g, c, i, j, k), intensity in zip(indices, intensities):
        if intensity / total_intensity < int_filter:
            int_rejected += intensity
            continue
        if vol_dict[c, i, j, k] / voxel_vols[i, j, k] < vol_filter:
            vol_rejected += intensity
            continue
        probs.append(intensity)
        e_indices.append(e_distr[g])
        c_values.append(c)
        x_indices.append(x_distr[i])
        y_indices.append(y_distr[j])
        z_indices.append(z_distr[k])    

    print('Rejection due to intensity filter: {0:.3e} g/sec ({1:.3e} %)'.format(
        int_rejected, int_rejected / total_intensity * 100)
    )
    print('Rejection due to volume filter:    {0:.3e} g/sec ({1:.3e} %)'.format(
        vol_rejected, vol_rejected / total_intensity * 100)
        )
    tot_rejected = vol_rejected + int_rejected
    print('Total rejection:                   {0:.3e} g/sec ({1:.3e} %)'.format(
        tot_rejected, tot_rejected / total_intensity * 100
    ))

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


def get_mesh_volumes(xbins, ybins, zbins):
    xbins = np.array(xbins)
    ybins = np.array(ybins)
    zbins = np.array(zbins)
    x_len = np.expand_dims(xbins[1:] - xbins[:-1], 1)
    y_len = np.expand_dims(ybins[1:] - ybins[:-1], 0)
    z_len = np.expand_dims(zbins[1:] - zbins[:-1], 0)
    return np.dot(np.expand_dims(np.dot(x_len, y_len), 2), z_len)
