# -*- coding: utf-8 -*-

from collections import deque, defaultdict

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
    template.create_scenario_template(text, kwargs['norm_flux'])
    files_text = template.fispact_files(kwargs['libs'])
    collapse_text = template.fispact_collapse(kwargs['libxs'], fmesh._data.shape[0])

    # Set configuration
    config = {}

    # Create input files
    if kwargs['approach'] == 'full':
        task_list = create_full_tasks(path, fmesh, masses, mat_dict)
    elif kwargs['approach'] == 'simple':
        task_list = create_simple_tasks(path)

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


def create_full_tasks(path, fmesh, masses, materials):
    """Creates fispact tasks.

    Parameters
    ----------
    path : Path
        Path, where tasks must be created.
    fmesh : FMesh
        Fmesh tally.
    masses : dict
        Masses of cells inside each voxel. c, i, j, k -> mass.
    materials : dict
        Dictionary of materials of every cell. cell_name -> material.
    
    Returns
    -------
    task_list : list
        List of tasks for execution. List of tuples: 
        (case_folder_name, [inventory_names])
    """
    raise NotImplementedError


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
    raise NotImplementedError


def create_lib_text(lib_dict):
    """Creates lib text.

    Parameters
    ----------
    lib_dict : dict
        A dictionary of libraries. lib_name -> path.
    
    Returns
    -------
    lib_text : str
        A text to be inserted into files file.
    """
    raise NotImplementedError

