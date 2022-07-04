# -*- coding: utf-8 -*-

import multiprocessing
from collections import defaultdict

from click import progressbar


def calculate_onecell_volumes(cell, mesh, min_volume):
    volumes = defaultdict(int)
    for i in range(mesh.shape[0]):
        for j in range(mesh.shape[1]):
            for k in range(mesh.shape[2]):
                box = mesh.get_voxel(i, j, k)
                vol = cell.shape.volume(box=box, min_volume=min_volume)
                if vol > 0:
                    index = (cell.name(), i, j, k)
                    volumes[index] += vol
    return volumes


def worker(input_queue, output_queue, mesh, min_volume):
    for cells in iter(input_queue.get, 'STOP'):
        for cell in cells:
            output_queue.put(calculate_onecell_volumes(cell, mesh, min_volume))


def calculate_volumes(cells, mesh, min_volume, threads=1, chunk=None):
    """Calculates volumes of model cells in every mesh voxel.

    Parameters
    ----------
    cells : list
        List of cells in mesh.
    mesh : RectMesh
        Mesh.
    min_volume : float
        Minimum volume for volume calculations.
    threads : int
        The number of threads to calculate volumes. Default: 1.
    chunk : int
        The number of cells to be passed to each worker. Default: None - 
        equals to the total number of cells divided by 200.

    Returns
    -------
    volumes : dict
        A dictionary of cell volumes. 
    """
    input_queue = multiprocessing.Queue()
    output_queue = multiprocessing.Queue()
    if chunk is None:
        chunk = max(1, int(len(cells) / 200))
    buffer = []
    task_count = 0
    for c in cells:
        buffer.append(c)
        if len(buffer) == chunk:
            input_queue.put(buffer)
            task_count += 1
            buffer = []
    if len(buffer) > 0:
        input_queue.put(buffer)
        task_count += 1
    
    processes = []
    for i in range(threads):
        processes.append(
            multiprocessing.Process(target=worker, args=(input_queue, output_queue, mesh, min_volume))
        )
    for p in processes:
        p.start()

    volumes = {}

    with progressbar(length=len(cells)) as bar:
        for i in range(len(cells)):
            result = output_queue.get()
            #cnames = set(key[0] for key in result.keys())
            volumes.update(result)
            bar.update(1)

    for _ in processes:
        input_queue.put('STOP')
    
    return volumes


if __name__ == '__main__':
    pass
