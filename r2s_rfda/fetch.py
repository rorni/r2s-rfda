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
    