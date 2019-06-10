# -*- coding: utf-8 -*-

import numpy as np
import mckit.source as mcs

from . import data


def create_source(gamma_data, timelab, start_distr=1):
    """Creates MCNP SDEF for gamma source.

    Parameters
    ----------
    gamma_data : SparseData
        Data on gamma yield for every cell and voxel.
    timelab : int
        Time label at which gamma source must be created, in sec.
    start_distr : int
        Starting SDEF distribution number.
    
    Returns
    -------
    sdef : str
        MCNP SDEF description.
    """
    label_index = gamma_data.axes.index('time')
    time_labels = gamma_data.labels[label_index]
    closest_lab = find_closest(timelab, time_labels)
    if closest_lab != timelab:
        print('Choosing the closest time label available: {0}'.format(closest_lab))
    time_selector = data.SparseData(('time',), (time_labels,), {(closest_lab,): 1})
    gamma_slice = gamma_data.tensor_dot(time_selector)
    source, intensity = activation_gamma_source(gamma_slice, start_distr)
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
    auxiliary_distributions = []
    aux_name = start_name + 5
    for var, label in zip(gamma_data.axes, gamma_data.labels):
        if var == 'cell':
            distr = label
        else:
            aux_name, distr = create_bin_distributions(label, aux_name)
        auxiliary_distributions.append(distr)

    probs = []
    indices = [[], [], [], [], []]
    for index in zip(*gamma_data.data.nonzero()):
        probs.append(gamma_data.data[index])
        for i, ind in enumerate(index):
            indices[i].append(auxiliary_distributions[i][ind])
    total_intensity = sum(probs)
    var_index = {var: i for i, var in enumerate(gamma_data.axes)}

    i = var_index['cell']
    cell_dist = mcs.Distribution(start_name, indices[i], probs, 'CEL')
    i = var_index['g_erg']
    e_dist = mcs.Distribution(start_name + 1, indices[i], cell_dist, 'ERG')
    i = var_index['xbins']
    x_dist = mcs.Distribution(start_name + 2, indices[i], cell_dist, 'X')
    i = var_index['ybins']
    y_dist = mcs.Distribution(start_name + 3, indices[i], cell_dist, 'Y')
    i = var_index['zbins']
    z_dist = mcs.Distribution(start_name + 4, indices[i], cell_dist, 'Z')

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


def find_closest(t, time_labels):
    """Finds the closest of time_labels to t.

    Parameters
    ----------
    t : int
        Time label.
    time_labels : list
        Time labels to search among which.

    Returns
    -------
    cl : int
        Closest time label.
    """
    i = np.searchsorted(time_labels, t)
    if i == 0:
        return time_labels[0]
    elif i == len(time_labels):
        return time_labels[-1]
    else:
        min_el = time_labels[i-1]
        max_el = time_labels[i]
        if t - min_el < max_el - t:
            return min_el
        else:
            return max_el

