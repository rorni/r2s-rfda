# -*- coding: utf-8 -*-
import re
from pathlib import Path
import subprocess
import json


def load_config(filename='.fispact_data.json', config='TENDL2014'):
    """Loads FISPACT data configuration.

    First it tries to find the specified file, and if it is not found, then
    it tries to find configuration file in user home folder.

    Parameters
    ----------
    filename : str
        Name of configureation file. Default: '.fispact_data.json'

    Returns
    -------
    data_path : dict
        A dictionary of FISPACT data paths.
    """
    path = Path(filename)
    if not path.exists():
        path = Path.home() / filename
    if not path.exists():
        return None
    else:
        with open(path) as fp:
            data = json.load(fp)
        base = Path(data['path'])
        data_path = {}
        for k, v in data[config].items():
            data_path[k] = str(base / v)
        return data_path


default_libs = load_config()


class FispactError(Exception):
    pass


class FispactSettings:
    """FISPACT settings object.

    Parameters
    ----------
    irr_profile : IrradiationProfile
        Irradiation profile.
    relax_profile : IrradiationProfile
        Relaxation profile.
    nat_reltol : float
        Relative tolerance to believe that elements have natural abundance.
        To force use of isotopic composition set nat_reltol to None.
        Default: 1.e-8.
    use_binary : bool
        Use binary libraries rather then text. Default: False.
    zero : bool
        If True, then time value is reset to zero after an irradiation.
    mind : float
        Indicate the minimum number of atoms which are regarded as significant
        for the output inventory. Default: 1.e+5
    use_fission : bool
        Causes to use fission reactions. If it is False - fission reactions are
        omitted. Default: False - not to use fission.
    half : bool
        If True, causes the half-lije of each nuclide to be printed in the
        output at all timesteps. Default: True.
    hazards : bool
        If True, causes data on potential ingestion and inhalation doses to be
        read and dose due to individual nuclides to be printed at all timesteps.
        Default: False.
    tab1, tab2, tab3, tab4: bool
        If True, causes output of the specific data into separate files.
        tab1 - number of atoms and grams of each nuclide;
        tab2 - activity (Bq) and dose rate (Sv per hour) of each nuclide;
        tab3 - ingestion and inhalation dose (Sv) of each nuclide;
        tab4 - gamma-ray spectrum (MeV per sec) and the number of gammas per group.
        All defaults to False.
    nostable : bool
        If True, printing of stable nuclides in the inventory is suppressed.
        Default: False
    inv_tol : (float, float)
        (atol, rtol) - absolute and relative tolerances for inventory
        calculations. Default: None - means default values remain (1.e+4, 2.e-3).
    path_tol : (float, float)
        (atol, rtol) - absolute and relative tolerances for pathways calculations.
        Default: None - means default values remain (1.e+4, 2.e-3).
    uncertainty : int
        Controls the uncertainty estimates and pathway information that are
        calculated and output for each time interval. Default: 0.
        0 - no pathways or estimates of uncertainty are calculated or output;
        1 - only estimates of uncertainty are output;
        2 - both estimates of uncertainty and the pathway information are output;
        3 - only the pathway information is output;
    """
    def __init__(self, irr_profile, nat_reltol=1.e-8, use_binary=False,
                 zero=True, mind=1.e+5, use_fission=False, half=True,
                 hazards=False, tab1=False, tab2=False, tab3=False, tab4=False,
                 nostable=False, inv_tol=None, path_tol=None, uncertainty=0):
        self.irr_profile = irr_profile
        self.nat_reltol = nat_reltol
        self.use_binary = use_binary
        self._kwargs = {
            'ZERO': zero, 'MIND': mind, 'USEFISSION': use_fission, 'HALF': half,
            'HAZARDS': hazards, 'TAB1': tab1, 'TAB2': tab2, 'TAB3': tab3,
            'TAB4': tab4, 'NOSTABLE': nostable, 'INVENTORY_TOLERANCE': inv_tol,
            'PATH_TOLERANCE': path_tol, 'UNCERTAINTY': uncertainty
        }

    def get_param(self, name):
        """Gets FISPACT inventory parameter.

        Parameters
        ----------
        name : str
            Parameter name.

        Returns
        -------
        value : object
            Parameter's value.
        """
        return self._kwargs.get(name)


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


def create_files(files='files', collapx='COLLAPX', fluxes='fluxes',
                 arrayx='ARRAYX', cwd=Path(), data=default_libs):
    """Creates new files file, that specifies fispact names and data.

    Parameters
    ----------
    files : str
        Name of file with list of libraries and other useful files. Default: files
    collapx : str
        Name of file of the collapsed cross sections. Default: COLLAPX
    fluxes : str
        Name of file with flux data. Default: fluxes.
    arrayx : str
        Name of arrayx file. Usually it is needed to be calculated only once.
    cwd : Path
        Working directory. In this directory files will be created. The folder
        must be exist. Default: current directory.
    data : dict
        A dictionary of FISPACT data files.

    Returns
    -------
    files : str
        Name of files file.
    """
    with open(cwd / files, mode='w') as f:
        for k, v in data.items():
            f.write(k + '  ' + v + '\n')
        f.write('fluxes  ' + fluxes + '\n')
        f.write('collapxi  ' + collapx + '\n')
        f.write('collapxo  ' + collapx + '\n')
        f.write('arrayx  ' + arrayx + '\n')
    return files


def create_convert(ebins, flux, convert='convert', fluxes='fluxes',
                   arb_flux='arb_flux', files='files.convert', cwd=Path()):
    """Creates file for fispact flux conversion to the 709 groups.

    Parameters
    ----------
    ebins : array_like[float]
        Energy bins.
    flux : array_like[float]
        Group flux.
    convert : str
        File name for convert input file.
    fluxes : str
        File name for converted neutron flux.
    arb_flux : str
        File name for input neutron flux.
    files : str
        File name for conversion data.
    cwd : Path
        Working directory. In this directory files will be created. The folder
        must be exist.

    Returns
    -------
    args : tuple
        Tuple of arguments for FISPACT.
    """
    with open(cwd / files, mode='w') as f:
        # f.write('ind_nuc  ' + DATA_PATH + LIBS['ind_nuc'] + '\n')
        f.write('fluxes  ' + fluxes + '\n')
        f.write('arb_flux  ' + arb_flux + '\n')

    with open(cwd / arb_flux, mode='w') as f:
        ncols = 6
        text = []
        for i, e in enumerate(reversed(ebins)):
            s = '\n' if (i + 1) % ncols == 0 else ' '
            text.append('{0:.6e}'.format(e * 1.e+6))  # Because fispact needs
            text.append(s)                            # eV, not MeV
        text[-1] = '\n'
        f.write(''.join(text))

        text = []
        for i, e in enumerate(reversed(flux)):
            s = '\n' if (i + 1) % ncols == 0 else ' '
            text.append('{0:.6e}'.format(e))
            text.append(s)
        text[-1] = '\n'
        f.write(''.join(text))
        f.write('{0}\n'.format(1))
        f.write('total flux={0:.6e}'.format(np.sum(flux)))

    with open(str(cwd / convert) + '.i', mode='w') as f:
        text = [
            '<< convert flux to 709 grout structure >>',
            'CLOBBER',
            'GRPCONVERT {0} 709'.format(len(flux)),
            'FISPACT',
            '* SPECTRAL MODIFICATION',
            'END',
            '* END'
        ]
        f.write('\n'.join(text))
    return convert, files


def create_collapse(collapse='collapse', use_binary=True, cwd=Path()):
    """Creates fispact file for cross-section collapse.

    Parameters
    ----------
    collapse : str
        Filename for collapse input file.
    use_binary : bool
        Use binary data rather text data.
    cwd : Path
        Working directory. In this directory files will be created.
        Default: current directory.

    Returns
    -------
    collapse : str
        Name of collapse file.
    """
    p = -1 if use_binary else +1
    with open(str(cwd / collapse) + '.i', mode='w') as f:
        text = [
            '<< collapse cross section data >>',
            'CLOBBER',
            'GETXS {0} 709'.format(p),
            'FISPACT',
            '* COLLAPSE',
            'END',
            '* END OF RUN'
        ]
        f.write('\n'.join(text))
    return collapse


def create_condense(condense='condense', cwd=Path()):
    """Creates fispact file to condense the decay and fission data.

    Parameters
    ----------
    condense : str
        Name of condense input file.
    cwd : Path
        Working directory. In this directory files will be created. Default:
        current directory.

    Returns
    -------
    condense : str
        Name of condense file.
    """
    with open(str(cwd / condense) + '.i', mode='w') as f:
        text = [
            '<< Condense decay data >>',
            'CLOBBER',
            'SPEK',
            'GETDECAY 1',
            'FISPACT',
            '* CONDENSE',
            'END',
            '* END OF RUN'
        ]
        f.write('\n'.join(text))
    return condense


def create_inventory(title, material, volume, flux, inventory='inventory',
                     settings=None, cwd=Path()):
    """Creates fispact file for inventory calculations.

    Parameters
    ----------
    title : str
        Title for the inventory.
    material : Material
        Material to be irradiated.
    volume : float
        Volume of the material.
    flux : float
        Total neutron flux.
    inventory : str
        File name for inventory input file.
    settings : FispactSettings
        Object that represents FISPACT inventory calculations parameters.
    cwd : Path
        Working directory. In this directory files will be created.
        Default: current directory.

    Returns
    -------
    inventory : str
        Name of inventory file.
    """
    if settings is None:
        settings = FispactSettings()
    # inventory header.
    text = [
        '<< {0} >>'.format(title),
        'CLOBBER',
        'GETXS 0',
        'GETDECAY 0',
        'FISPACT',
        '* {0}'.format(title)
    ]
    # Initial conditions.
    # ------------------
    # Material
    text.extend(print_material(material, volume, tolerance=settings.nat_reltol))
    # Calculation parameters.
    text.append('MIND  {0:.5e}'.format(settings.get_param('MIND')))
    if settings.get_param('USEFISSION'):
        text.append('USEFISSION')
    if settings.get_param('HALF'):
        text.append('HALF')
    if settings.get_param('HAZARDS'):
        text.append('HAZARDS')
    if settings.get_param('TAB1'):
        text.append('TAB1 1')
    if settings.get_param('TAB2'):
        text.append('TAB2 1')
    if settings.get_param('TAB3'):
        text.append('TAB3 1')
    if settings.get_param('TAB4'):
        text.append('TAB4 1')
    if settings.get_param('NOSTABLE'):
        text.append('NOSTABLE')
    inv_tol = settings.get_param('INVENTORY_TOLERANCE')
    if inv_tol:
        text.append('TOLERANCE  0  {0:.5e}  {1:.5e}'.format(*inv_tol))
    path_tol = settings.get_param('PATH_TOLERANCE')
    if path_tol:
        text.append('TOLERANCE  1  {0:.5e}  {1:.5e}'.format(*path_tol))
    uncertainty = settings.get_param('UNCERTAINTY')
    if uncertainty:
        text.append('UNCERTAINTY {0}'.format(uncertainty))
    # Irradiation and relaxation profiles
    text.extend(settings.irr_profile.output(flux))
    # Footer
    text.append('END')
    text.append('* END of calculations')
    # Save to file
    with open(str(cwd / inventory) + '.i', mode='w') as f:
        f.write('\n'.join(text))
    return inventory


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

