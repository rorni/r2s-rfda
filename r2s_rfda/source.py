# -*- coding: utf-8 -*-

import numpy as np
import mckit.source as mcs

from . import data


def create_source(gamma_data, start_distr=1):
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
#    label_index = gamma_data.axes.index('time')
#    time_labels = gamma_data.labels[label_index]
#    if offset:
#        timelab += time_labels[offset]
#    closest_lab = find_closest(timelab, time_labels)
#    if closest_lab != timelab:
#        print('Choosing the closest time label available: {0}'.format(closest_lab))
#    time_selector = data.SparseData(('time',), (time_labels,), {(closest_lab,): 1})
#    gamma_slice = gamma_data.tensor_dot(time_selector)
    source, intensity = activation_gamma_source(gamma_data, start_distr)
    sdef = 'C total gamma intensity = {0:.5e}\n{1}'.format(intensity, source.mcnp_repr())
    return sdef


def activation_gamma_source(gamma_data, start_name=1):
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
    # energy
    aux_name, e_distr = create_bin_distributions(gamma_data.gbins, aux_name)
    # xbins
    aux_name, x_distr = create_bin_distributions(gamma_data.xbins, aux_name)
    # ybins
    aux_name, y_distr = create_bin_distributions(gamma_data.ybins, aux_name)
    # zbins
    aux_name, z_distr = create_bin_distributions(gamma_data.zbins, aux_name)
    
    probs = []
    e_indices = []
    x_indices = []
    y_indices = []
    z_indices = []
    c_values = []
    for (g, c, i, j, k), intensity in gamma_data.iter_nonzero():
        probs.append(intensity)
        e_indices.append(e_distr[g])
        c_values.append(c)
        x_indices.append(x_distr[i])
        y_indices.append(y_distr[j])
        z_indices.append(z_distr[k])
    total_intensity = sum(probs)

    cell_dist = mcs.Distribution(start_name, c_values, probs, 'CEL')
    e_dist = mcs.Distribution(start_name + 1, e_indices, cell_dist, 'ERG')
    x_dist = mcs.Distribution(start_name + 2, x_indices, cell_dist, 'X')
    y_dist = mcs.Distribution(start_name + 3, y_indices, cell_dist, 'Y')
    z_dist = mcs.Distribution(start_name + 4, z_indices, cell_dist, 'Z')

    src_params = {
        'PAR': 2, 'EFF': 1.e-2, 'CEL': cell_dist, 'ERG': e_dist, 
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

