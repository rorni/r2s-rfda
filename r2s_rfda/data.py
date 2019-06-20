# -*- coding: utf-8 -*-

import numpy as np
from scipy.sparse import csr_matrix
from collections import defaultdict


class GammaFrame:
    """Represents time frame of gamma intensity data.

    Parameters
    ----------
    data : numpy.ndarray
        Gamma data.
    sindex : SpatialIndex
        Spatial data index.
    gbins : array_like
        Gamma energy bin boundaries.
    mesh : RectMesh
        Spatial mesh.

    Methods
    -------

    """
    def __init__(self, data, sindex, timelabel, gbins, mesh):
        self._data = csr_matrix(data)
        self._sindex = sindex
        self._timelabel = timelabel
        self._gbins = gbins
        self._mesh = mesh

    @property
    def xbins(self):
        return self._mesh._xbins

    @property
    def ybins(self):
        return self._mesh._ybins
    
    @property
    def zbins(self):
        return self._mesh._zbins

    @property
    def mesh(self):
        return self._mesh
    
    @property
    def gbins(self):
        return self._gbins

    @property
    def timelabel(self):
        return self._timelabel

    @property
    def spatial_index(self):
        return self._sindex

    def __getitem__(self, index):
        """Gets element.

        Parameters
        ----------
        index : tuple(int)
            Index of element. g, c, i, j, k.
        
        Returns
        -------
        value : float
            Value.
        """
        g, c, i, j, k = index
        q = self._sindex.indices(c=c, i=i, j=j, k=k)
        return self._data[g, q]  

    def iter_nonzero(self):
        """Iterates through all nonzero elements of the gamma data.

        Returns
        -------
        index : tuple(int)
            Index of the data. g, c, i, j, k.
        value : float
            Value.
        """
        for g, q in zip(*self._data.nonzero()):
            c, i, j, k = self._sindex.label(q)
            v = self._data[g, q]
            yield (g, c, i, j, k), v


class SpatialIndex:
    """Spatial index of mesh geometry.

    Parameters
    ----------
    indices : iterable
        A list of index tuples: (c, i, j, k).

    Methods
    -------
    label(index)
        Gets labels that correspond to the index.
    indices(c, i, j, k)
        Gets indices that correspond to the labels.
    """
    def __init__(self, indices):
        self._c_labels = defaultdict(set)
        self._i_labels = defaultdict(set)
        self._j_labels = defaultdict(set)
        self._k_labels = defaultdict(set)
        self._labels = tuple(x for x in sorted(indices))
        for q, (c, i, j, k) in enumerate(self._labels):
            self._c_labels[c].add(q)
            self._i_labels[i].add(q)
            self._j_labels[j].add(q)
            self._k_labels[k].add(q)  
    
    def cells(self):
        return tuple(sorted(self._c_labels.keys()))

    def __len__(self):
        return len(self._labels)     

    def label(self, index):
        """Gets labels, that correspond to the index.

        Parameters
        ----------
        index : int
            Index.
        
        Returns
        -------
        c : int 
            Cell name.
        i, j, k : int
            Voxel labels.
        """
        return self._labels[index]

    def indices(self, c=None, i=None, j=None, k=None):
        """Gets indices that correspond to the labels.

        Parameters
        ----------
        c : int
            Cell label. Default: None.
        i, j, k : int
            Voxel labels. Default: None.

        Returns
        -------
        index : list
            Indices, that corresponds to the specified labels.
        """
        candidates = set(range(len(self._labels)))
        if c:
            candidates.intersection_update(self._c_labels.get(c, set()))
        if i:
            candidates.intersection_update(self._i_labels.get(i, set()))
        if j:
            candidates.intersection_update(self._j_labels.get(j, set()))
        if k:
            candidates.intersection_update(self._k_labels.get(k, set()))
        return list(sorted(candidates))

    def __iter__(self):
        return iter(self._labels)


