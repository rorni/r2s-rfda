# -*- coding: utf-8 -*-

from mckit import read_mcnp
from mckit.parser.meshtal_parser import read_meshtal


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
    # 
    raise NotImplementedError


def calculate_volumes(model, mesh, min_volume):
    """Calculates volumes of model cells in every mesh voxel.

    Parameters
    ----------
    model : Universe
        MCNP model.
    mesh : RectMesh
        Mesh.
    min_volume : float
        Minimum volume for volume calculations.

    Returns
    -------
    volumes : SparseData
        Cell volumes. 
    """
    raise NotImplementedError


def get_materials(model, cells):
    """Gets materials and densities of cells.

    Parameters
    ----------
    model : Universe
        MCNP model.
    cells : list
        A list of cell names.

    Returns
    -------
    materials : SparseData
        Cell-material matrix.
    densities : SparseData
        Cell densities.
    """
    raise NotImplementedError


def create_full_tasks(path, template, fmesh, masses, materials):
    """Creates fispact tasks.

    Parameters
    ----------
    path : Path
        Path, where tasks must be created.
    template : str
        Fispact inventory input file template.
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


def create_simple_tasks(path, template, ebins, materials, flux, mass):
    """Creates fispact tasks for superposition method.

    Parameters
    ----------
    path : Path
        Path, where tasks must be created.
    template : str
        Fispact inventory input file template.
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

