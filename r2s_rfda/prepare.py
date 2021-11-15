# -*- coding: utf-8 -*-

from collections import deque, defaultdict

import numpy as np
from click import progressbar
from mckit import read_mcnp
from mckit.parser.meshtal_parser import read_meshtal
from mckit.material import AVOGADRO
from mckit.transformation import Transformation

from . import template
from . import data
from . import utils


def parse_transforamtion(input):
    if input[0] == '*':
        indegrees = True
    else:
        indegrees = False
    input = input.strip('*() ')
    entities = [float(x) for x in input.split()]
    translation = entities[:3]
    if len(entities) == 3:
        rotation = None
    else:
        rotation = entities[3:]
    return translation, rotation, indegrees    


def create_tasks(path, **kwargs):
    """Creates tasks for fispact.

    Parameters
    ----------
    path : Path
        Path, where tasks must be created.
    **kwargs : dict
        A dictionary of input data.
    
    Returns
    -------
    config : dict
        Task configuration.
    """
    model = read_mcnp_input(kwargs['mcnp_name'])
    
    fmesh = read_fmesh_tally(kwargs['fmesh_name'], kwargs['tally_name'], kwargs['transform'])

    # set templates
    zero_index = init_templates(
        kwargs['inventory'], kwargs['norm_flux'], kwargs['libs'], 
        kwargs['libxs'], fmesh._data.shape[0]
    )

    bbox = fmesh.mesh.bounding_box()
    print('Selecting cells ...')
    cells = select_cells(model, bbox)

    print('Calculate volumes ...')
    vol_dict = calculate_volumes(cells, fmesh.mesh, kwargs['min_volume'])

    mat_dict = get_materials(cells)
    den_dict = get_densities(cells)
    mass_dict = get_masses(vol_dict, den_dict)

    # Set configuration
    config = {
        'mesh': fmesh.mesh, 'volumes': vol_dict, 'masses': mass_dict, 
        'approach': kwargs['approach'], 'zero': zero_index
    }

    # Create input files
    print('Creating input files ...')
    if kwargs['approach'] == 'full':
        task_list, index_output = create_full_tasks(
            path, fmesh, mass_dict, mat_dict, den_dict
        )
    elif kwargs['approach'] == 'simple':
        F0 = np.max(fmesh._data)
        M0 = max(mass_dict.values())
        ebins = fmesh._ebins

        config['alpha'] = fmesh._data / F0
        config['beta'] = {k: v / M0 for k, v in mass_dict.items()}
        config['c2m'] = {c: m.name() for c, m in mat_dict.items()}

        mats = {m.name(): m for m in mat_dict.values()}
        task_list, index_output = create_simple_tasks(
            path, ebins, mats, F0, M0
        )

    config['task_list'] = task_list
    config['index_output'] = index_output
    return config


def read_mcnp_input(inp_filename):
    print('Reading MCNP model ({0}) ...'.format(inp_filename))
    return read_mcnp(inp_filename)


def read_fmesh_tally(fmesh_filename, tally_name, transform):
    print('Reading meshtal file ({0}) ...'.format(fmesh_filename))
    tallies = read_meshtal(fmesh_filename)
    tally = tallies[tally_name]
    if transform is not None:
        transl, rot, indegrees = parse_transforamtion(transform)
        tr = Transformation(transl, rot, indegrees=indegrees, name=1)
        tally.mesh.transform(tr)
    return tally


def init_templates(inv_filename, norm_flux, libs, libxs, nerg_groups):
    with open(inv_filename) as f:
        text = f.read()
    template.init_inventory_template(text, norm_flux)
    template.init_files_template(libs)
    template.init_collapse_template(libxs, nerg_groups)
    return utils.find_zero_step(text)


def calculate_volumes(cells, mesh, min_volume):
    """Calculates volumes of model cells in every mesh voxel.

    Parameters
    ----------
    cells : list
        List of cells in mesh.
    mesh : RectMesh
        Mesh.
    min_volume : float
        Minimum volume for volume calculations.

    Returns
    -------
    volumes : dict
        A dictionary of cell volumes. 
    """
    volumes = defaultdict(int)
    nx, ny, nz = mesh.shape
    with progressbar(length=nx*ny*nz) as bar:
        for i in range(mesh.shape[0]):
            for j in range(mesh.shape[1]):
                for k in range(mesh.shape[2]):
                    box = mesh.get_voxel(i, j, k)
                    for c in cells:
                        vol = c.shape.volume(box=box, min_volume=min_volume)
                        if vol > 0:
                            index = (c.name(), i, j, k)
                            volumes[index] += vol
                    bar.update(1)
    return volumes


def select_cells(model, box):
    """Finds all cells that intersect the box.

    Parameters
    ----------
    model : Universe
        The model to be checked.
    box : Box
        Box to be checked.
    
    Returns
    -------
    cells : list
        A list of selected cells.
    """
    cells = []
    cells_to_check = deque(c for c in model)
    while len(cells_to_check) > 0:
        c = cells_to_check.popleft()
        fill_opt = c.options.get('FILL', None)
        test = c.shape.test_box(box)
        if test == -1:
            continue
        if fill_opt:
            u = fill_opt['universe']
            tr = fill_opt.get('transform', None)
            if tr:
                u = u.transform(tr)
            for uc in u:
                cells_to_check.append(uc.intersection(c))
        elif c.material():
            cells.append(c)
    return cells


def get_materials(cells):
    """Gets materials of cells.

    Parameters
    ----------
    cells : list
        A list of cells.

    Returns
    -------
    materials : dict
        Dictionary of materials. cell_name -> material.
    """
    materials = {}
    for c in cells:
        mat = c.material()
        name = c.name()
        materials[name] = mat.composition
    return materials


def get_densities(cells):
    """Gets densities of cells.

    Parameters
    ----------
    cells : list
        A list of cells.
    
    Returns
    -------
    densities : dict
        A dictionary of cell densities. cell_name -> density [g/cc].
    """
    densities = {}
    for c in cells:
        mat = c.material()
        name = c.name()
        densities[name] = mat.density
    return densities


def get_masses(vol_dict, den_dict):
    """Calculates masses of cell pieces in every voxel.
     
    Parameters
    ----------
    vol_dict : dict
        c, i, j, k -> vol
    den_dict : dict
        c -> density

    Returns
    -------
    masses : dict
        c, i, j, k -> mass
    """
    masses = {}
    for (c, i, j, k), vol in vol_dict.items():
        masses[(c, i, j, k)] = vol * den_dict[c]
    return masses


def create_full_tasks(path, fmesh, masses, materials, densities):
    """Creates fispact tasks.

    Parameters
    ----------
    path : Path
        Path, where tasks must be created.
    fmesh : FMesh
        Fmesh tally.
    masses : dict
        A dictionary of cell masses in each voxel. c, i, j, k -> mass.
    materials : dict
        Dictionary of materials of every cell. cell_name -> material.
    densities : dict
        A dictionary of cell densities of every cell. cell_name -> density.
    
    Returns
    -------
    task_list : list
        List of tasks for execution. List of tuples: 
        (case_folder_name, [inventory_names])
    index_output : dict
        A dictionary (c, i, j, k) -> output_file_name.
    """
    task_list = []
    index_output = {}
    ebins = fmesh._ebins
    fdata = fmesh._data
    spatial_to_cell = defaultdict(list)
    for (c, i, j, k), mass in masses.items():
        spatial_to_cell[(i, j, k)].append((c, mass))
    
    for (i, j, k), cell_mass in spatial_to_cell.items():
        spectrum = fdata[:, i, j, k]
        flux = np.sum(spectrum)

        task_item = prepare_folder(
            path, 'case-{0}-{1}-{2}'.format(i, j, k), ebins, spectrum
        )

        for c, mass in cell_mass:
            den = densities[c]
            mat_text = material_description(materials[c], mass, density=den)
            inventory_name = 'inventory_{0}'.format(c)
            add_inventory_case(
                task_item, inventory_name, flux, mat_text
            )
            index_output[(c, i, j, k)] = task_item[0] / (inventory_name + '.out')
        task_list.append(task_item)
        
    return task_list, index_output


def prepare_folder(path, name, ebins, spectrum):
    """Prepares folder for FISPACT case.

    Parameters
    ----------
    path : Path
        Path, where tasks must be created.
    name : str
        Name of the particular case.
    ebins : array_like
        Neutron energy bin boundaries.
    spectrum : array_like
        Neutron group spectrum.
    
    Returns
    -------
    task_item : tuple
        folder_path, list of tasks to run.
    """
    folder = path / name
    folder.mkdir()

    files = folder / 'files'
    files.write_text(template.fispact_files())
    collapse = folder / 'collapse.i'
    collapse.write_text(template.fispact_collapse())
    arb_flux = folder / 'arb_flux'

    ebins = ebins.copy()
    ebins[0] = 1.e-11
    arb_flux.write_text(template.create_arbflux_text(ebins, spectrum))

    return folder, ['collapse']


def add_inventory_case(task_item, name, flux, mat):
    """Adds new task case to task_item.

    Parameters
    ----------
    task_item : tuple
        folder path, case list.
    name : str
        Inventory file name.
    flux : float
        Nominal flux value.
    mat : str
        Material description.
    """
    folder, cases = task_item
    inventory = folder / (name + '.i')
    inventory.write_text(template.fispact_inventory(flux, mat))
    cases.append(name)


def create_simple_tasks(path, ebins, materials, flux, mass):
    """Creates fispact tasks for superposition method.

    Parameters
    ----------
    path : Path
        Path, where tasks must be created.
    ebins : array_like
        Energy bins.
    materials : dict
        A dictionary of materials. material_name -> material.
    flux : float
        Value of flux, assumed for all calculations.
    mass : float
        Value of mass, assumed for all calculations.

    Returns
    -------
    task_list : list
        List of tasks to be executed. List of tuples:
        (case_folder_name, [inventory_names])
    index_output : dict
        A dictionary (n_erg_bin, mat_name) -> output_file_name.
    """
    task_list = []
    index_output = {}
    nf = len(ebins) - 1
    for i in range(nf):
        spectrum = np.zeros(nf)
        spectrum[i] = flux

        task_item = prepare_folder(
            path, 'case-{0}'.format(i), ebins, spectrum
        )

        for name, mat in materials.items():
            mat_text = material_description(mat, mass)
            inventory_name = 'inventory_{0}'.format(name)
            add_inventory_case(
                task_item, inventory_name, flux, mat_text
            )
            index_output[(i, name)] = task_item[0] / (inventory_name + '.out')
        task_list.append(task_item)

    return task_list, index_output


def material_description(material, mass, density=1.0):
    """Creates FISPACT material description.

    Parameters
    ----------
    material : mckit.Composition
        Material.
    mass : float
        Mass of the material.
    density : float
        Density of the material. Default: 1.0 g/cc.
    
    Returns
    -------
    mat_text : str
        Fispact material description.
    """
    lines = deque()
    expanded_mat = material.expand()
    tot_atoms = mass / expanded_mat.molar_mass * AVOGADRO
    for elem, conc in expanded_mat:
        elem_name = elem.fispact_repr()
        atom_qty = tot_atoms * conc
        lines.append('  {0} {1:.4e}'.format(elem_name, atom_qty))
    lines.appendleft('FUEL {0}'.format(len(lines)))
    lines.appendleft('DENSITY {0:.4e}'.format(density))
    return '\n'.join(lines)
