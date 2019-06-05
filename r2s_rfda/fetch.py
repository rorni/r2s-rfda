# -*- coding: utf-8 -*-

import pypact as pp
import numpy as np

from itertools import accumulate


def collect(path, config):
    """Collects data from files.

    Parameters
    ----------
    path : Path
        Path to folder, where to store results.
    config : dict
        Dictionary of configuration data.
    """
    raise NotImplementedError


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
        A dictionary of the number of atoms. (time_label, isotope) -> atoms.
    activity : dict
        A dictionary of the isotope activities. (time_label, isotope) -> activity.
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
            name = nuc.element + str(nuc.isotope)
            atoms[(time_labels[-1], name)] = nuc.atoms
            activity[(time_labels[-1], name)] = nuc.activity
    return time_labels, ebins, atoms, activity, gamma_yield
