# -*- coding: utf-8 -*-

import re
from pkg_resources import resource_filename
import numpy as np


def read_template(temp_name):
    with open(resource_filename(__name__, 'templates/' + temp_name)) as f:
        template = f.read()
    return template


files_temp = read_template('files.temp')
collapse_temp = read_template('collapse.temp')
condense_temp = read_template('condense.temp')
inventory_temp = None
flux_coeffs = None

order = [
    'ind_nuc', 'xs_endf', 'xs_endfb', 'prob_tab', 'fy_endf', 'sf_endf', 'dk_endf',
    'hazards', 'clear', 'a2data', 'absorp'
]


def create_scenario_template(inptemp, norm_flux):
    """Creates new template with replaced fluxes in irradiation scenario.

    New template is stored in module local variable since the template will not
    be changed for particular task. The irradiation profile is also stored at
    module level.

    Parameters
    ----------
    inptemp : str
        Input template of inventory input file.
    norm_flux : float
        Flux value for normalization.
    """
    global inventory_temp
    global flux_coeffs
    pat = re.compile('FLUX +[0-9]+.[0-9]+E.[0-9]+')
    res = pat.split(inptemp)
    mats = pat.findall(inptemp)
    flux_coeffs = []
    for i, mat in enumerate(mats):
        res.insert(2*i+1, 'FLUX {{{0}}}'.format(i))
        flux_coeffs.append(float(mat[4:]) / norm_flux)
    inventory_temp = ''.join(res)
    flux_coeffs = np.array(flux_coeffs)


def fispact_files(datalib):
    """Creates files text.

    Parameters
    ----------
    datalib : dict
        A dictionary of libraries to be used in FISPACT calculations.
    
    Returns
    -------
    text : str
        Text of files file.
    """
    # for name in order:
    
    # datalib - словарь названий библиотек, и путей к ним.
    # Надо эти записи соединить в строки. Каждая библиотека на новой строке.
    # Причем пробелы между названием библиотеки и путем надо вставить так, 
    # чтобы выровнить пути. Между самым длинным названием библиотеки и ее 
    # путем должно быть два пробела. См. соответствующий тест.


def fispact_collapse(libxs, nestrc):
    """Creates collapse input file.

    Parameters
    ----------
    libxs : int
        If -1 - to use binary library, if 1 - use text library.
    nestrc : int
        The number of energy groups in neutron spectrum.
    
    Returns
    -------
    text : str
        Text of collapse file.
    """
    return collapse_temp.format(nestrc=nestrc, libxs=libxs)


def fispact_inventory(flux, material):
    """Creates text of inventory input file.

    Parameters
    ----------
    flux : float
        Nominal flux value for the scenario at particular point.
    material : str
        Material description.

    Returns
    -------
    text : str
        Text of inventory file.
    """
    raise NotImplementedError


def create_arbflux_text(ebins, flux):
    """Creates file for fispact flux conversion to the 709 groups.

    Parameters
    ----------
    ebins : array_like[float]
        Energy bins in MeV.
    flux : array_like[float]
        Group flux.

    Returns
    -------
    arb_flux : str
        Text for arb_flux file.
    """
    ncols = 6
    text = []
    for i, e in enumerate(reversed(ebins)):
        s = '\n' if (i + 1) % ncols == 0 else ' '
        text.append('{0:.6e}'.format(e * 1.e+6))  # Because fispact needs
        text.append(s)                            # eV, not MeV
    text[-1] = '\n'
   
    for i, e in enumerate(reversed(flux)):
        s = '\n' if (i + 1) % ncols == 0 else ' '
        text.append('{0:.6e}'.format(e))
        text.append(s)
    text[-1] = '\n'
    text.append('1\n')
    text.append('total flux={0:.6e}'.format(np.sum(flux)))

    return ''.join(text)
