# -*- coding: utf-8 -*-

import re
from pkg_resources import resource_filename
import numpy as np


def read_template(temp_name):
    with open(resource_filename(__name__, 'templates/' + temp_name)) as f:
        template = f.read()
    return template


files_temp = None     # read_template('files.temp')
collapse_temp = None  # read_template('collapse.temp')
condense_temp = None  # read_template('condense.temp')
inventory_temp = None
flux_coeffs = None

order = [
    'ind_nuc', 'xs_endf', 'xs_endfb', 'prob_tab', 'fy_endf', 'sf_endf', 'dk_endf',
    'hazards', 'clear', 'a2data', 'absorp'
]


FRACTION = r'\.'
EXPONENT = r'([eE][-+]?\d+)'
INT_NUMBER = r'(\d+)'
FLT_NUMBER = r'(' + \
             INT_NUMBER + r'|' +\
             INT_NUMBER + r'?' + FRACTION + INT_NUMBER + EXPONENT + r'?|' +\
             INT_NUMBER + FRACTION + r'?' + EXPONENT + r'|' + \
             INT_NUMBER + FRACTION + r')(?=[ \n-+])'
             

def init_inventory_template(inptemp, norm_flux):
    """Initialize new template with replaced fluxes in irradiation scenario.

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
    flux_pattern = re.compile('(FLUX +)', flags=re.IGNORECASE)
    zero_pattern = re.compile('0[ \n]')
    float_pattern = re.compile(FLT_NUMBER, flags=re.IGNORECASE)

    substrings = flux_pattern.split(inptemp)
    flux_coeffs = []
    try_number = False
    result = []
    i = 0
    for string in substrings:
        if try_number:
            if zero_pattern.match(string):
                result.append(string)
            else:
                match = float_pattern.match(string)
                if not match:
                    raise ValueError('Scenario template contains incorrect data')
                flux_coeffs.append(float(match.group(0)) / norm_flux)
                result.append('{{{0}}}'.format(i))
                i += 1
                result.append(string[match.end(0):])
        else:
            result.append(string)
        if flux_pattern.fullmatch(string):
            try_number = True
        else:
            try_number = False
    inventory_temp = ''.join(result)
    flux_coeffs = np.array(flux_coeffs)


def init_files_template(datalib):
    """Initializes files template.

    Parameters
    ----------
    datalib : dict
        A dictionary of libraries to be used in FISPACT calculations.
    """
    global files_temp
    max_len = max(map(len, datalib.keys()))
    lib_str = []
    for name in order:
        if name in datalib.keys():
            spaces = ' ' * (max_len - len(name) + 2)
            lib_str.append(name + spaces + datalib[name])
    temp = read_template('files.temp')
    files_temp = temp.format(datalib='\n'.join(lib_str))


def init_collapse_template(libxs, nestrc):
    """Initializes collapse input file.

    Parameters
    ----------
    libxs : int
        If -1 - to use binary library, if 1 - use text library.
    nestrc : int
        The number of energy groups in neutron spectrum.
    """
    global collapse_temp
    temp = read_template('collapse.temp')
    collapse_temp = temp.format(nestrc=nestrc, libxs=libxs)


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
    fluxes = map('{0:.4e}'.format, flux * flux_coeffs)
    return inventory_temp.format(*fluxes, material=material)


def fispact_files():
    """Gets fispact files text."""
    return files_temp


def fispact_collapse():
    """Gets fispact collapse text."""
    return collapse_temp


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
    text.append('1.0\n')
    text.append('total flux={0:.6e}'.format(np.sum(flux)))

    return ''.join(text)
