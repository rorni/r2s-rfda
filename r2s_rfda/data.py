# -*- coding: utf-8 -*-

import sparse
import numpy as np


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
    replace_axes() 
        Copies the SparseData object and replaces specific axes.
    """
    def __init__(self, axes, labels, data):
        if len(axes) != len(labels):
            raise ValueError('Inconsistent axes and labels')
        self._axes = tuple(axes)
        self._labels = tuple(tuple(x) for x in labels)
        if isinstance(data, dict):
            enum_rules = create_enum_rules(labels)
            coords = np.empty((len(axes), len(data.items())))
            spdata = np.empty(len(data.items()))
            for i, (k, v) in enumerate(data.items()):
                coords[:, i] = create_index(k, enum_rules)
                spdata[i] = v
            shape = tuple(len(l) for l in labels)
            self._data = sparse.COO(coords, data=spdata, shape=shape)
        elif isinstance(data, sparse.COO):
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
        convolution_labels = set(self.axes).intersection(data.axes)
        si = self.find_indices(convolution_labels)
        di = data.find_indices(convolution_labels)
        conv_data = sparse.tensordot(self.data, data.data, axes=(si, di))
        conv_axes = []
        conv_labels = []
        for i, lab in enumerate(self.axes):
            if i not in si:
                conv_axes.append(lab)
                conv_labels.append(self.labels[i])
        for i, lab in enumerate(data.axes):
            if i not in di:
                conv_axes.append(lab)
                conv_labels.append(data.labels[i])
        return SparseData(conv_axes, conv_labels, conv_data)

    def find_indices(self, labels):
        labels = labels.copy()
        indices = []
        for i, ax in enumerate(self._axes):
            if ax in labels:
                indices.append(i)
                labels.remove(ax)
        return tuple(indices)

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
        sset = set(self.axes)
        dset = set(data.axes)
        if sset < dset:
            return data.multiply(self)
        elif sset >= dset:
            diff = sset.difference(dset)
            s_ind = enumerate_labels(self.axes)
            dshape = [len(l) for l in data.labels]
            daxes = list(data.axes)
            dlabels = list(data.labels)
            for dl in diff:
                dshape.insert(0, len(self.labels[s_ind[dl]]))
                daxes.insert(0, dl)
                dlabels.insert(0, self.labels[s_ind[dl]])
            if len(dshape) > len(data.axes):
                data_arr = data._data.broadcast_to(dshape)
            else:
                data_arr = data._data
            d_ind = enumerate_labels(daxes)
            pert = [s_ind[l] for l in daxes]
            new_data = self._data.transpose(pert) * data_arr
            print(daxes, dlabels)
            return SparseData(daxes, dlabels, new_data)
        else: 
            raise ValueError('Incorrect shapes.')

    def replace_axes(self, **axeslabs):
        """Make a copy of data and replaces axes.

        Parameters
        ----------
        axeslabs : dict
            A dictionary of pairs (new_axis_name, axis_values).

        Returns
        -------
        result : SparseData
            New SparseData object.
        """
        new_ax = []
        new_lab = []
        for ax, labs in zip(self._axes, self._labels):
            if ax in axeslabs.keys():
                nax, nlab = axeslabs[ax]
                new_ax.append(nax)
                new_lab.append(nlab)
            else:
                new_ax.append(ax)
                new_lab.append(labs)
        return SparseData(new_ax, new_lab, self._data)

    @property
    def axes(self):
        """Names of axes."""
        return self._axes

    @property
    def labels(self):
        """Axes labels."""
        return self._labels

    @property
    def data(self):
        """Data itself."""
        return self._data


def enumerate_labels(labels):
    return {label: i for i, label in enumerate(labels)}

def create_enum_rules(labels):
    enum_rules = []
    for label_list in labels:
        rule = enumerate_labels(label_list)
        enum_rules.append(rule)
    return enum_rules


def create_index(label, rule):
    return [rule[i][l] for i, l in enumerate(label)]
