# -*- coding: utf-8 -*-

import sparse


class SparseData:
    """Represents multidimensional sparse data.

    Parameters
    ----------
    axes : list[str]
        A list of axis labels.
    bins : dict[list]
        A dictionary of axis bins. key - is axis label. Value - bin boundaries
        or labels along the axis.
    shape : tuple
        Data shape. It is needed to judge if axis has been boundaries or labels.
    data : sparse.COO or dict
        Data. If it is already an array, then it is just copied. If it is a dict
        it is used to construct sparse data array.

    Methods
    -------
    tensor_dot(data)
        Tensor dot product with other SparseData object.
    multiply(data)
        Element-wise multiplication of the two arrays. 
    """
    def __init__(self, axes, bins, shape, data):
        self._axes = axes
        self._bins = bins
        self._shape = shape
        if isinstance(data, dict):
            pass
        elif isinstance(data, shape.COO):
            self._data = data
        else:
            raise TypeError('Unknown data type. data must be either dict or SparseData instance')

    def tensor_dot(self, data):
        """Tensor dot product with other SparseData object.

        It takes into account axis labels of both SparseData objects and shapes.
        It finds coincident labels and do tensor dot product along those axes.
        If either there is no coincident axis labels or dimensions of such axes
        are different, exception TypeError is raised.

        Parameters
        ----------
        data : SparseData
            Another SparseData instance.

        Returns
        -------
        result : SparseData
            Tensor dot product.
        """
        raise NotImplementedError

    def multiply(self, data):
        """Do element-wise multiplication of two tensors.

        Dimensions are not necessary to be coincident, but one of the tensors
        must be a subset of another. In the later case the subset tensor will
        be extended.

        Parameters
        ----------
        data : SparseData
            Another SparseData instance.

        Returns
        -------
        result : SparseData
            Element-wise multiplication of two tensors.
        """
        raise NotImplementedError

    @property
    def axes(self):
        raise NotImplementedError

    @property
    def bins(self):
        raise NotImplementedError

    @property
    def data(self):
        raise NotImplementedError

    @property
    def shape(self):
        raise NotImplementedError
