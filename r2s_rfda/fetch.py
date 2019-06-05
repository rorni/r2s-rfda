# -*- coding: utf-8 -*-

import pypact as pp
import numpy as np
import pickle

from itertools import accumulate


def collect(path, config):
    """Collects all data from inventory files and writes total files on disk.

    Parameters
    ----------
    path : Path
        Path to folder, where to store results.
    config : dict
        Dictionary of configuration data.
    """
    A = {}
    N = {}
    G = {}
    for index, casepath in config['index_output'].items():
        time_labels, ebins, atoms, activity, gamma_yield = read_fispact_output(casepath)
        for (t, nuc), act in activity.items():
            A[(t, nuc, *index)] = act
        for (t, nuc), number in atoms.items():
            N[(t, nuc, *index)] = number
        for t, gamma_ar in gamma_yield.items():
            for i, gam in enumerate(gamma_ar):
                G[(t, i, *index)] = gam
    with open(path / 'activity.dat', 'bw') as f:
        pickle.dump(A, f, pickle.HIGHEST_PROTOCOL)
    with open(path / 'atoms.dat', 'bw') as f:
        pickle.dump(N, f, pickle.HIGHEST_PROTOCOL)
    with open(path / 'gamma.dat', 'bw') as f:
        pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)


def load_gamma(path):
    """Loads gamma yield distribution.

    Parameters
    ----------
    path : Path
        Path to search.
    
    Returns
    -------
    gamma : SparseData
        Gamma yield distribution.
    """
    raise NotImplementedError


def apply_superposition(tensor, material, alpha, beta):
    """

    Parameters
    ----------
    tensor : SparseData object
        Activation data obtained for F0 and M0
    material : SparseData objects
        Material-cell map
    alpha : SparseData object
        Flux normilize coeffs
    beta : SparseData object
        Mass normilize coeffs

    Returns
    -------

    """
    tensor = tensor.tensor_dot(alpha)
    tensor = tensor.tensor_dot(material)
    tensor = tensor.multiply(beta)
    return tensor


def read_fispact_output(path):
    """Reads FISPACT output file.

    Parameters
    ----------
    path : Path
        Path to output file.

    Returns
    -------
    time_labels : list
        Labels of time moments.
    ebins : list
        list of gamma energy bin boundaries.
    atoms : dict
        A dictionary of the number of atoms. (time_label, nuclide) -> atoms.
    activity : dict
        A dictionary of the nuclide activities. (time_label, nuclide) -> activity.
    gamma_yield : dict
        A dictionary of the decay gamma intensity. time_label ->
        gamma yield group spectrum [gamma/sec]
    """
    with pp.Reader(path) as output:
        idata = output.inventory_data
    ebins = np.array(idata[0].gamma_spectrum.boundaries)
    eners = 0.5 * (ebins[1:] + ebins[:-1])
    durations = []
    time_labels = []
    atoms = {}
    activity = {}
    gamma_yield = {}
    for i, ts in enumerate(idata):
        durations.append(ts.duration)
        time_labels.append(np.array(durations).sum())
        gamma_yield[time_labels[-1]] = np.array(ts.gamma_spectrum.values) / eners
        for nuc in ts.nuclides:
            name = nuc.element + str(nuc.isotope) + nuc.state
            atoms[(time_labels[-1], name)] = nuc.atoms
            activity[(time_labels[-1], name)] = nuc.activity
    return time_labels, ebins, atoms, activity, gamma_yield
