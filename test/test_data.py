# -*- coding: utf-8 -*-

import pytest
import sparse


from r2s_rfda import data


@pytest.mark.parametrize('axes, bins, shape, sdata, answer', [
    (
        ('cell', 'i', 'j'), ([4, 2, 3, 1], [0, 1, 2], [0, 1]), (4, 3, 2),
        {(1, 0, 0): 3, (1, 2, 0): 2, (2, 1, 1): 4, (3, 1, 0): 5, (4, 0, 0): 1},
        {(3, 0, 0): 3, (3, 2, 0): 2, (1, 1, 1): 4, (2, 1, 0): 5, (0, 0, 0): 1}
    )
])
def test_create(axes, bins, shape, sdata, answer):
    sd = data.SparseData(axes, bins, shape, sdata)
    assert sd.axes == axes
    assert sd.bins == bins
    assert sd.shape == shape
    for index, value in answer.items():
        assert sd.data[index] == value
    assert sd.data.nnz == len(answer)


@pytest.mark.parametrize('tensor1, tensor2, answer', [
    (
        (
            ('cell', 'i', 'j'), ([1, 2, 3, 4], [0, 1, 2], [0, 1]), (4, 3, 2),
            {(1, 0, 0): 3, (1, 2, 0): 2, (2, 1, 1): 4, (3, 1, 0): 5, (4, 0, 0): 1}
        ),
        (
            ('cell', 'cell'), ([1, 2, 3, 4], [1, 2, 3, 4]), (4, 4), 
            {(1, 1): 2, (2, 2): 0.5, (3, 3): 4, (4, 4): 0.1}
        ),
        (
            ('cell', 'i', 'j'), ([1, 2, 3, 4], [0, 1, 2], [0, 1]), (4, 3, 2),
            {(0, 0, 0): 6, (0, 2, 0): 4, (1, 1, 1): 2, (2, 1, 0): 20, (3, 0, 0): 0.1}
        )
    )
])
def test_tensor_dot(tensor1, tensor2, answer):
    t1 = data.SparseData(*tensor1)
    t2 = data.SparseData(*tensor2)
    result = t1.tensor_dot(t2)
    assert result.axes == answer[0]
    assert result.bins == answer[1]
    assert result.shape == answer[2]
    for index, value in answer[3].items():
        assert result.data[index] == value
    assert result.data.nnz == len(answer[3])


@pytest.mark.parametrize('tensor1, tensor2, answer', [
    (
        (
            ('cell', 'i', 'j'), ([1, 2, 3, 4], [0, 1, 2], [0, 1]), (4, 3, 2),
            {(1, 0, 0): 3, (1, 2, 0): 2, (2, 1, 1): 4, (3, 1, 0): 5, (4, 0, 0): 1}
        ),
        (
            ('i', 'j'), ([0, 1, 2], [0, 1]), (3, 2), 
            {(0, 0): 2, (2, 0): 3, (1, 0): 4}
        ),
        (
            ('cell', 'i', 'j'), ([1, 2, 3, 4], [0, 1, 2], [0, 1]), (4, 3, 2),
            {(0, 0, 0): 6, (0, 2, 0): 6, (3, 1, 0): 20, (4, 0, 0): 2}
        )
    )
])
def test_multiply(tensor1, tensor2, answer):
    t1 = data.SparseData(*tensor1)
    t2 = data.SparseData(*tensor2)
    result = t1.multiply(t2)
    assert result.axes == answer[0]
    assert result.bins == answer[1]
    assert result.shape == answer[2]
    for index, value in answer[3].items():
        assert result.data[index] == value
    assert result.data.nnz == len(answer[3])
