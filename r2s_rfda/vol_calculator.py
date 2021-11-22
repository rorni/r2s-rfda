# -*- coding: utf-8 -*-

import multiprocessing
from collections import defaultdict


_mesh_obj = None
_min_volume = 1.e-3


def volume_calculator_initilizer(*args):
    global _mesh_obj
    global _min_volume
    _mesh_obj = args[0]
    print('setup mesh: {0}'.format(_mesh_obj.shape))
    _min_volume = args[1]


def calculate_volumes(cell):
    volumes = defaultdict(int)
    for i in range(_mesh_obj.shape[0]):
        for j in range(_mesh_obj.shape[1]):
            for k in range(_mesh_obj.shape[2]):
                box = _mesh_obj.get_voxel(i, j, k)
                vol = cell.shape.volume(box=box, min_volume=_min_volume)
                if vol > 0:
                    index = (cell.name(), i, j, k)
                    volumes[index] += vol
    return volumes
