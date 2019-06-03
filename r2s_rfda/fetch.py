# -*- coding: utf-8 -*-

import pypact


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
        A dictionary of the decay gamma intensity. (time_label, en_label) -> gamma yield 
        [gamma/sec]
    """
    pass
