import numpy as np


def flatten_volume(volumes, index):
    """Converts volumes to the flattened form.

    Parameters
    ----------
    volumes : dict
        A dictionary of cell volumes for every voxel: (i, j, k, cell)->volume.
    index : SparseIndex
        Represents flattening rules.

    Returns
    -------
    flat_vol : numpy.ndarray
        Flattened array of volumes.
    """
    result = np.empty(len(index))
    for (i, j, k, c), vol in volumes.items():
        n = index.get_flatten_index(i, j, k, c)
        result[n] = vol
    return result


def flatten_flux(flux, index):
    """Converts flux array to the flattened form.

    Parameters
    ----------
    flux : numpy.ndarray
        Input flux array.
    index : SparseIndex
        Represents flattening rules.

    Returns
    -------
    flat_flux : numpy.ndarray
        Flattened array of fluxes.
    """
    e = flux.shape[0]
    result = np.empty((len(index), e))
    for n, (i, j, k, c) in enumerate(index):
        result[n, :] = flux[:, i, j, k]
    return result


def flatten_materials(index):
    """Gets vector of flattened materials.

    Parameters
    ----------
    index : SparseIndex
        Represents flattening rules.

    Returns
    -------
    materials : numpy.ndarray
        Materials.
    """
    materials = np.empty(len(index), dtype=object)
    for n, (i, j, k, c) in enumerate(index):
        materials[n] = c.material()
    return materials


class SparseIndex:
    """Represents sparse data flatten index.

    Parameters
    ----------
    volume_data : dict
        A dictionary of cell volumes for every voxel: (i, j, k, cell)->volume.

    Methods
    -------
    get_flatten_index(i, j, k, cell)
        Gets flatten index of sparse data.
    get_voxel_index(index)
        Gets voxel and cell, that correspond to the flatten index.
    get_voxel_indices(i, j, k)
        Gets a set of flattened indices that belong to the voxel.
    get_cells(i, j, k)
        Gets all cells that are contained in the voxel.
    voxels()
        Iterator over voxel indices.
    """
    def __init__(self, volume_data):
        self._vc = {}
        for index, ((i, j, k, cell), vol) in enumerate(volume_data.items()):
            if vol > 0:
                self._vc[(i, j, k, cell)] = index
        n = len(self._vc)
        self._index_i = np.empty(n, dtype=int)
        self._index_j = np.empty(n, dtype=int)
        self._index_k = np.empty(n, dtype=int)
        self._cells = np.empty(n, dtype=object)
        for (i, j, k, cell), index in self._vc.items():
            self._index_i[index] = i
            self._index_j[index] = j
            self._index_k[index] = k
            self._cells[index] = cell

    def __len__(self):
        return self._index_i.size

    def __iter__(self):
        return zip(self._index_i, self._index_j, self._index_k, self._cells)

    def voxels(self):
        """Gets iterator over all contained voxels."""
        done = set()
        for i, j, k, c in self:
            index = i, j, k
            if index not in done:
                done.add(index)
                yield index

    def get_flatten_index(self, i, j, k, cell):
        """Gets flatten index, that corresponds to the cell and voxel specified.

        Parameters
        ----------
        i, j, k : int
            Voxel indices.
        cell : Body
            Cell.

        Returns
        -------
        index : int
            Index in the flattened array. If such element does not exists,
            returns None.
        """
        return self._vc.get((i, j, k, cell), None)

    def get_voxel_index(self, index):
        """Gets voxel and cell, that correspond to flatten index.

        Parameters
        ----------
        index : int
            Index in flattened array.

        Returns
        -------
        i, j, k : int
            Voxel indices.
        cell : Body
            Cell.
        """
        i = self._index_i[index]
        j = self._index_j[index]
        k = self._index_k[index]
        cell = self._cells[index]
        return i, j, k, cell

    def get_cells(self, i, j, k):
        """Gets all cells that are contained in the voxel.

        Parameters
        ----------
        i, j, k : int
            Indices of the voxel.

        Returns
        -------
        cells : list[Body]
            List of cells contained in the voxel.
        """
        indices = self.get_voxel_indices(i, j, k)
        cells = [self._cells[ind] for ind in indices]
        return cells

    def get_voxel_indices(self, i, j, k):
        """Gets all indices that belong to the voxel.

        Parameters
        ----------
        i, j, k : int
            Indices of the voxel.

        Returns
        -------
        indices : set
            Flatten indices of the voxel.
        """
        i_ind = set(np.where(self._index_i == i)[0])
        j_ind = set(np.where(self._index_j == j)[0])
        k_ind = set(np.where(self._index_k == k)[0])
        indices = i_ind.intersection(j_ind).intersection(k_ind)
        return indices


def encode_materials(materials):
    """Enumerate all materials found in cells.

    Parameters
    ----------
    materials : array_like[Material]
        List of materials.

    Returns
    -------
    mat_codes : dict
        A dictionary of material codes (Material->int).
    """
    code = 1
    mat_codes = {}
    for mat in materials:
        if mat not in mat_codes.keys():
            mat_codes[mat] = code
            code += 1
    return mat_codes
