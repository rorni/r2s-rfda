# -*- coding: utf-8 -*-

from itertools import accumulate

import pypact as pp
import numpy as np
import pickle
from click import progressbar

from . import data


def collect(path, config, index):
    """Collects all data from inventory files and writes total files on disk.

    Parameters
    ----------
    path : Path
        Path to folder, where to store results.
    config : dict
        Dictionary of configuration data.
    index : int
        Start time index for data fetch.
    """
    A_dict = {}
    N_dict = {}
    G_dict = {}
    nuclides = set()
    print('Start data collection ...')
    with progressbar(config['index_output'].items()) as bar:
        for index, casepath in bar:
            time_labels, ebins, atoms, activity, gamma_yield = read_fispact_output(casepath, index)
            for (t, nuc), act in activity.items():
                A_dict[(t, nuc, *index)] = act
                nuclides.add(nuc)
            for (t, nuc), number in atoms.items():
                N_dict[(t, nuc, *index)] = number
            for t, gamma_ar in gamma_yield.items():
                for i, gam in enumerate(gamma_ar):
                    G_dict[(t, i, *index)] = gam
    
    nuclides = list(sorted(nuclides))
    g_labels = list(range(len(ebins) - 1))

    print('Creating sparse data arrays ...')
    if config['approach'] == 'full':
        a_axes = ('time', 'nuclide', 'cell', 'i', 'j', 'k')
        a_labels = (
            time_labels, nuclides, config['cell_labels'], config['i_labels'],
            config['j_labels'], config['k_labels']
        )
        n_axes = ('time', 'nuclide', 'cell', 'i', 'j', 'k')
        n_labels = (
            time_labels, nuclides, config['cell_labels'], config['i_labels'],
            config['j_labels'], config['k_labels']
        )
        g_axes = ('time', 'g', 'cell', 'i', 'j', 'k')
        g_labels = (
            time_labels, g_labels, config['cell_labels'], config['i_labels'],
            config['j_labels'], config['k_labels']
        )
    else:
        a_axes = ('time', 'nuclide', 'n_erg', 'material')
        a_labels = (
            time_labels, nuclides, config['en_labels'], config['mat_labels']
        )
        n_axes = ('time', 'nuclide', 'n_erg', 'material')
        n_labels = (
            time_labels, nuclides, config['en_labels'], config['mat_labels']
        )
        g_axes = ('time', 'g', 'n_erg', 'material')
        g_labels = (
            time_labels, g_labels, config['en_labels'], config['mat_labels']
        )

    A = create_sparse_data(A_dict, a_axes, a_labels, 'activity')
    N = create_sparse_data(N_dict, n_axes, n_labels, 'atoms')
    G = create_sparse_data(G_dict, g_axes, g_labels, 'gamma')

    if config['approach'] == 'full':
        print('Making superposition ...')
        A = apply_superposition(A, config['material'], config['alpha'], config['beta'])
        N = apply_superposition(N, config['material'], config['alpha'], config['beta'])
        G = apply_superposition(G, config['material'], config['alpha'], config['beta'])

    print('Replacing axes ...')
    A = A.replace_axes(
        i=('xbins', config['xbins']), j=('ybins', config['ybins']), 
        k=('zbins', config['zbins'])
    )
    N = N.replace_axes(
        i=('xbins', config['xbins']), j=('ybins', config['ybins']), 
        k=('zbins', config['zbins'])
    )
    G = G.replace_axes(
        g=('g_erg', ebins),
        i=('xbins', config['xbins']), j=('ybins', config['ybins']), 
        k=('zbins', config['zbins'])
    )

    print('Saving results ...')
    with open(path / 'activity.dat', 'bw') as f:
        pickle.dump(A, f, pickle.HIGHEST_PROTOCOL)
    with open(path / 'atoms.dat', 'bw') as f:
        pickle.dump(N, f, pickle.HIGHEST_PROTOCOL)
    with open(path / 'gamma.dat', 'bw') as f:
        pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)


def create_sparse_data(X_dict, axes, labels, message):
    print('  Creating {0} array ...'.format(message))
    X = data.SparseData(axes, labels, X_dict)
    X_dict.clear()
    return X


def apply_superposition(tensor, material, alpha, beta):
    """Applies superposition to material-flux results.

    Parameters
    ----------
    tensor : SparseData
        Activation data obtained for F0 and M0
    material : SparseData
        Material-cell map
    alpha : SparseData
        Flux normilize coeffs
    beta : SparseData
        Mass normilize coeffs

    Returns
    -------
    result : SparseData
        Result data.
    """
    tensor = tensor.tensor_dot(alpha)
    tensor = tensor.tensor_dot(material)
    tensor = tensor.multiply(beta)
    return tensor


def read_fispact_output(path, index=None):
    """Reads FISPACT output file.

    Parameters
    ----------
    path : Path
        Path to output file.
    index : int
        Starting index for data collection.

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
        if i < index:
            continue
        time_labels.append(int(np.array(durations).sum()))
        gamma_yield[time_labels[-1]] = np.array(ts.gamma_spectrum.values) / eners
        for nuc in ts.nuclides:
            name = nuc.element + str(nuc.isotope) + nuc.state
            atoms[(time_labels[-1], name)] = nuc.atoms
            activity[(time_labels[-1], name)] = nuc.activity
    return time_labels, ebins, atoms, activity, gamma_yield


def load_data(path, name):
    """Loads data from path.

    Parameters
    ----------
    path : Path
        Path to output file.
    name : str
        Data name.
    
    Returns
    -------
    data : SparseData
        Output data.
    """
    filename = path / (name + '.dat')
    with open(filename, 'br') as f:
        data = pickle.load(f)
    return data
