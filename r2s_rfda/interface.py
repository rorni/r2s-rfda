# -*- coding: utf-8 -*-
import re
from pathlib import Path
import subprocess
from pkg_resources import resource_filename

import numpy as np


def read_template(temp_name):
    with open(resource_filename(__name__, 'data/' + temp_name)) as f:
        template = f.read()
    return template


files_temp = read_template('files.temp')
collapse_temp = read_template('collapse.temp')
condense_temp = read_template('condense.temp')


class FispactError(Exception):
    pass


def run_fispact(input_file, files='files', cwd=None, verbose=True):
    """Runs FISPACT code.

    If run ends with errors, then FispactError exception is raised.

    Parameters
    ----------
    input_file : str
        The name of input file.
    files : str
        The name of FISPACT files file. Default: 'files'.
    cwd : Path-like or str
        Working directory. Default: None.
    verbose : bool
        Whether to print calculation status to stdout.

    Returns
    -------
    status : str
        Run status message.
    """
    status = subprocess.check_output(
        ['fispact', input_file, files], encoding='utf-8', cwd=cwd
    )
    if verbose:
        print(status)
    check_fispact_status(status)
    return status


def check_fispact_status(text):
    """Raises FispactError exception if FATAL ERROR presents in output.

    Parameters
    ----------
    text : str
        Text to be checked.
    """
    match = re.search('^.*run +terminated.*$', text, flags=re.MULTILINE)
    if match:
        raise FispactError(match.group(0))


def create_fispact_input(name, cwd, template, *args, **kwargs):
    """Creates fispact input file from the template.

    Parameters
    ----------
    name : str
        Name of FISPACT input file to be created.
    cwd : Path
        Working directory. In this directory files will be created. The folder
        must exist.
    template : str
        Template string with format specifiers. 
    *args : list
        A list of positional symbols that are to be inserted into template.
    **kwargs : dict
        A dictionary of named symbols that are to be inserted into template.
    """
    text = template.format(*args, **kwargs)
    with open(cwd / name, mode='w') as f:
        f.write(text)


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


def print_material(material, volume, tolerance=1.e-8):
    """Produces FISPACT description of the material.

    Parameters
    ----------
    material : Material
        Material to be irradiated.
    volume : float
        Volume of the material.
    tolerance : float
        Relative tolerance to believe that isotopes have natural abundance.
        If None - no checking is performed and FUEL keyword is used.

    Returns
    -------
    text : list[str]
        List of words.
    """
    text = ['DENSITY {0}'.format(material.density)]
    composition = []
    if tolerance is not None:
        nat_comp = material.composition.natural(tolerance)
        if nat_comp is not None:
            mass = volume * material.density / 1000    # Because mass must be specified in kg.
            for e in nat_comp.elements():
                composition.append((e, nat_comp.get_weight(e) * 100))
            text.append('MASS {0:.5} {1}'.format(mass, len(composition)))
    else:
        nat_comp = None

    if tolerance is None or nat_comp is None:
        exp_comp = material.composition.expand()
        tot_atoms = volume * material.concentration
        # print('tot atoms ', tot_atoms, 'vol ', volume, 'conc ', material.concentration)
        for e in exp_comp.elements():
            composition.append((e, exp_comp.get_atomic(e) * tot_atoms))
        text.append('FUEL  {0}'.format(len(composition)))

    for e, f in sorted(composition, key=lambda x: -x[1]):
        # print(e, f)
        text.append('  {0:2s}   {1:.5e}'.format(e.fispact_repr(), f))
    return text

