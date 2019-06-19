# -*- coding: utf-8 -*-

import numpy as np
from collections import defaultdict


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


