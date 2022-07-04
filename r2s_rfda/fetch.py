# -*- coding: utf-8 -*-

from itertools import accumulate

import pypact as pp
import numpy as np
import pickle
from click import progressbar
from scipy.sparse import csr_matrix
from collections import defaultdict

from . import data


def collect(path, config):
    """Collects all data from inventory files and writes total files on disk.

    Parameters
    ----------
    path : Path
        Path to folder, where to store results.
    config : dict
        Dictionary of configuration data.
    """
    sp_index = data.SpatialIndex(config['volumes'].keys())

    A_dict = defaultdict(lambda: defaultdict(dict))
    N_dict = defaultdict(lambda: defaultdict(dict))
    G_dict = defaultdict(lambda: defaultdict(dict))
    nuclides = set()
    print('Start data collection ...')
    with progressbar(config['index_output'].items()) as bar:
        for index, casepath in bar:
            time_labels, ebins, atoms, activity, gamma_yield = read_fispact_output(casepath)
            for (t, nuc), act in activity.items():
                A_dict[t][nuc][index] = act
                nuclides.add(nuc)
            for (t, nuc), number in atoms.items():
                N_dict[t][nuc][index] = number
            for t, gamma_ar in gamma_yield.items():
                for i, gam in enumerate(gamma_ar):
                    G_dict[t][i][index] = gam
    
    g_labels = list(range(len(ebins) - 1))
    nuclides = list(sorted(nuclides))

    result_conf = prepare_result_folder(path, time_labels)
    with open(path / 'result.cfg', 'bw') as f:
        pickle.dump(result_conf, f, pickle.HIGHEST_PROTOCOL)

    if config['approach'] == 'simple':
        flux_coeffs = flatten_flux_coeffs(sp_index, config['alpha'])
        mat_labels = list(sorted(set(config['c2m'].values())))
        mass_coeffs = flatten_mass_coeffs(sp_index, config['beta'], config['c2m'], mat_labels)

    print('Preparing gamma data ...')
    with progressbar(G_dict.items()) as bar:
        for t, frame_dict in bar:
            if config['approach'] == 'full':
                frame = get_full_frame(frame_dict, sp_index, g_labels)
            else:
                frame = get_simple_frame(frame_dict, flux_coeffs, mass_coeffs, mat_labels, g_labels)
            frame_obj = data.GammaFrame(frame, sp_index, t, ebins, config['mesh'])
            save_data(result_conf['gamma'][t], frame_obj)

    print('Preparing activity data ...')
    with progressbar(A_dict.items()) as bar:
        for t, frame_dict in bar:
            if config['approach'] == 'full':
                frame = get_full_frame(frame_dict, sp_index, nuclides)
            else:
                frame = get_simple_frame(frame_dict, flux_coeffs, mass_coeffs, mat_labels, nuclides)
            frame_obj = data.GammaFrame(frame, sp_index, t, nuclides, config['mesh'])
            save_data(result_conf['activity'][t], frame_obj)

    print('Preparing atoms data ...')
    with progressbar(N_dict.items()) as bar:
        for t, frame_dict in bar:
            if config['approach'] == 'full':
                frame = get_full_frame(frame_dict, sp_index, nuclides)
            else:
                frame = get_simple_frame(frame_dict, flux_coeffs, mass_coeffs, mat_labels, nuclides)
            frame_obj = data.GammaFrame(frame, sp_index, t, nuclides, config['mesh'])
            save_data(result_conf['atoms'][t], frame_obj)


def get_full_frame(frame_dict, s_index, var_labels):
    var_index = {v: i for i, v in enumerate(var_labels)}
    frame = np.zeros((len(var_labels), len(s_index)))
    for g, data_dict in frame_dict.items():
        g_i = var_index[g]
        for (c, i, j, k), value in data_dict.items():
            q = s_index.indices(c=c, i=i, j=j, k=k)[0]
            frame[g_i, q] = value
    return frame


def get_simple_frame(frame_dict, flux_coeffs, mass_coeffs, mat_labels, var_labels):
    g_data = {}
    shape = (len(mat_labels), flux_coeffs.shape[0])
    for g, data_dict in frame_dict.items():
        data_arr = dict_to_array(data_dict, shape, mat_labels)
        g_data[g] = apply_superposition(data_arr, flux_coeffs, mass_coeffs)
    frame = produce_slice_array(g_data, var_labels)
    return frame

            
def prepare_result_folder(path, timelabels):
    folder = path / 'results'
    folder.mkdir()
    data = {'gamma': {}, 'atoms': {}, 'activity': {}}
    for t in timelabels:
        data['gamma'][t] = folder / 'gamma_{0}.dat'.format(t)
        data['atoms'][t] = folder / 'atoms_{0}.dat'.format(t)
        data['activity'][t] = folder / 'activity_{0}.dat'.format(t)
    return data


def dict_to_array(data_dict, shape, mat_labels):
    mat_index = {m: i for i, m in enumerate(mat_labels)}
    result = np.zeros(shape)
    for (i, name), value in data_dict.items():
        j = mat_index[name]
        result[j, i] = value
    return result


def flatten_mass_coeffs(sindex, mass_coeffs, c2m, mat_labels):
    mat_index = {m: i for i, m in enumerate(mat_labels)}
    data = np.zeros((len(mat_labels), len(sindex)))
    for q, (c, i, j, k) in enumerate(sindex):
        coeff = mass_coeffs[(c, i, j, k)]
        m = c2m[c]
        data[mat_index[m], q] = coeff
    return data


def flatten_flux_coeffs(sindex, flux_coeffs):
    ne = flux_coeffs.shape[0]
    result = np.zeros((ne, len(sindex)))
    for q, (c, i, j, k) in enumerate(sindex):
        result[:, q] = flux_coeffs[:, i, j, k]
    return result


def produce_slice_array(data_dict, labels):
    lind = {lab: i for i, lab in enumerate(labels)}
    g = len(labels)
    n = len(next(iter(data_dict.values())))
    result = np.zeros((g, n))
    for k, v in data_dict.items():
        i = lind[k]
        result[i, :] = v
    return result


def apply_superposition(data, flux, mass):
    """Applies superposition to data piece.

    Parameters
    ----------
    data : np.ndarray
        Calculated data. m x n
    flux : np.ndarray
        Flux data. n x q
    mass : np.ndarray
        Mass data. m x q
    
    Returns
    -------
    result : np.ndarray
        Resulting data. len=q
    """
    result = np.dot(data, flux)
    result *= mass
    return np.sum(result, axis=0)


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
        time_labels.append(int(np.array(durations).sum()))
        gamma_yield[time_labels[-1]] = np.array(ts.gamma_spectrum.values) / eners
        for nuc in ts.nuclides:
            name = nuc.element + str(nuc.isotope) + nuc.state
            atoms[(time_labels[-1], name)] = nuc.atoms
            activity[(time_labels[-1], name)] = nuc.activity
    return time_labels, ebins, atoms, activity, gamma_yield


def load_data(path):
    """Loads data from path.

    Parameters
    ----------
    path : Path
        Path to output file.
    
    Returns
    -------
    data : SparseData
        Output data.
    """
    with open(path, 'br') as f:
        data = pickle.load(f)
    return data


def load_result_config(path):
    """Loads result configuration."""
    filename = path / 'result.cfg'
    with open(filename, 'br') as f:
        data = pickle.load(f)
    return data


def save_data(path, data):
    """Saves data."""
    with open(path, 'bw') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
