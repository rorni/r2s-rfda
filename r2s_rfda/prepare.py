# -*- coding: utf-8 -*-

from collections import deque, defaultdict

import numpy as np
from mckit import read_mcnp
from mckit.parser.meshtal_parser import read_meshtal

from . import template
from . import data


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
    mcnp_name = kwargs['mcnp_name']
    print('Reading MCNP model ({0}) ...'.format(mcnp_name))
    model = read_mcnp(mcnp_name)

    fmesh_name = kwargs['fmesh_name']
    print('Reading meshtal file ({0}) ...'.format(fmesh_name))
    tallies = read_meshtal(fmesh_name)
    fmesh = tallies[kwargs['tally']]

    bbox = fmesh.mesh.bounding_box()
    print('Selecting cells ...')
    cells = select_cells(model, bbox)

    print('Calculate volumes ...')
    vol_dict = calculate_volumes(cells, fmesh.mesh, kwargs['min_volume'])

    mat_dict = get_materials(cells)
    den_dict = get_densities(cells)

    # Label creation
    cell_labels = sorted([c.name() for c in cells])
    mat_labels = sorted(list(set(m.name() for m in mat_dict.values())))
    i_labels = list(range(fmesh.mesh.shape[0]))
    j_labels = list(range(fmesh.mesh.shape[1]))
    k_labels = list(range(fmesh.mesh.shape[2]))

    ext_den_dict = {(c, c): rho for c, rho in den_dict.items()}
    density = data.SparseData(
        ('cell', 'cell'), (cell_labels, cell_labels), ext_den_dict
    )

    cell_to_mat_dict = {(c, m.name()): 1 for c, m in mat_dict.items()}
    material = data.SparseData(
        ('cell', 'material'), (cell_labels, mat_labels), cell_to_mat_dict
    )

    volumes = data.SparseData(
        ('cell', 'i', 'j', 'k'), (cell_labels, i_labels, j_labels, k_labels),
        vol_dict
    )

    masses = density.tensor_dot(volumes)

    # set templates
    with open(kwargs['inventory']) as f:
        text = f.read()
    template.init_inventory_template(text, kwargs['norm_flux'])
    template.init_files_template(kwargs['libs'])
    template.init_collapse_template(kwargs['libxs'], fmesh._data.shape[0])

    # Set configuration
    config = {}

    # Create input files
    if kwargs['approach'] == 'full':
        task_list = create_full_tasks(path, fmesh, vol_dict, mat_dict, den_dict)
    elif kwargs['approach'] == 'simple':
        F0 = np.max(fmesh._data)
        M0 = masses.data.max()
        ebins = fmesh._ebins
        mats = {m.name(): m for m in mat_dict.values()}
        task_list = create_simple_tasks(path, ebins, mats, F0, M0)

    config['task_list'] = task_list
    return config


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
    for i in range(mesh.shape[0]):
        for j in range(mesh.shape[1]):
            for k in range(mesh.shape[2]):
                box = mesh.get_voxel(i, j, k)
                for c in cells:
                    vol = c.shape.volume(box=box, min_volume=min_volume)
                if vol > 0:
                    index = (c.name(), i, j, k)
                    volumes[index] += vol
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


def create_full_tasks(path, fmesh, volumes, materials, densities):
    """Creates fispact tasks.

    Parameters
    ----------
    path : Path
        Path, where tasks must be created.
    fmesh : FMesh
        Fmesh tally.
    volumes : dict
        A dictionary of cell volumes in each voxel. c, i, j, k -> volume.
    materials : dict
        Dictionary of materials of every cell. cell_name -> material.
    densities : dict
        A dictionary of cell densities of every cell. cell_name -> density.
    
    Returns
    -------
    task_list : list
        List of tasks for execution. List of tuples: 
        (case_folder_name, [inventory_names])
    """
    task_list = []
    ebins = fmesh._ebins
    fdata = fmesh._data
    spatial_to_cell = defaultdict(list)
    for (c, i, j, k), vol in volumes.items():
        spatial_to_cell[(i, j, k)].append((c, vol))
    
    for (i, j, k), cell_vols in spatial_to_cell.items():
        spectrum = fdata[:, i, j, k]
        flux = np.sum(spectrum)

        folder = path / ('case-{0}-{1}-{2}'.format(i, j, k))
        folder.mkdir()

        files = folder / 'files'
        files.write_text(template.fispact_files())
        collapse = folder / 'collapse.i'
        collapse.write_text(template.fispact_collapse())
        arb_flux = folder / 'arb_flux'
        arb_flux.write_text(template.create_arbflux_text(ebins, spectrum))

        case_list = ['collapse.i']
        for c, vol in cell_vols.items():
            den = densities[c]
            mat_text = material_description(materials[c], den * vol, density=den)
            inventory_name = 'inventory_{0}.i'.format(c)
            inventory = folder / inventory_name
            inventory.write_text(template.fispact_inventory(flux, mat_text))
            case_list.append(inventory_name)
        task_list.append((folder, case_list))
        
    return task_list


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
    """
    task_list = []
    nf = len(ebins) - 1
    for i in range(nf):
        f = np.zeros(nf)
        f[i] = flux
        folder = path / ('case-{0}'.format(i))
        folder.mkdir()

        files = folder / 'files'
        files.write_text(template.fispact_files())
        collapse = folder / 'collapse.i'
        collapse.write_text(template.fispact_collapse())
        arb_flux = folder / 'arb_flux'
        arb_flux.write_text(template.create_arbflux_text(ebins, f))

        case_list = ['collapse.i']
        for name, mat in materials.items():
            mat_text = material_description(mat, mass)
            inventory_name = 'inventory_{0}.i'.format(name)
            inventory = folder / inventory_name
            inventory.write_text(template.fispact_inventory(flux, mat_text))
            case_list.append(inventory_name)
        task_list.append((folder, case_list))

    return task_list


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
    raise NotImplementedError
