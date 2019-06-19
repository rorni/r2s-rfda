# -*- coding: utf-8 -*-

import pytest


from r2s_rfda import data


@pytest.fixture(scope='module')
def index():
    indices = [
        (2, 1, 0, 3),  # 1
        (2, 2, 0, 5),  # 2 
        (4, 0, 0, 4),  # 3
        (4, 0, 0, 5),  # 4
        (1, 1, 0, 3),  # 0
        (5, 1, 0, 3),  # 6
        (5, 0, 0, 4)   # 5
    ]
    return data.SpatialIndex(indices)


@pytest.mark.parametrize('labels, answer', [
    ({'c': 2, 'i': 1, 'j': 0, 'k': 3}, [1]), 
    ({'c': 2, 'i': 2, 'j': 0, 'k': 5}, [2]),
    ({'c': 4, 'i': 0, 'j': 0, 'k': 4}, [3]),  
    ({'c': 4, 'i': 0, 'j': 0, 'k': 5}, [4]), 
    ({'c': 1, 'i': 1, 'j': 0, 'k': 3}, [0]), 
    ({'c': 5, 'i': 0, 'j': 0, 'k': 3}, [6]), 
    ({'c': 5, 'i': 0, 'j': 0, 'k': 4}, [5]),
    ({'c': 2}, [1, 2]), ({'c': 4}, [3, 4]), ({'c': 5}, [5, 6]), ({'c': 1}, [0]),
    ({'i': 1}, [0, 1, 6]), ({'i': 1, 'j': 0, 'k': 3}, [0, 1, 6]), 
    ({'i': 0, 'j': 0, 'k': 4}, [3, 5]), ({'c': 2, 'k': 3}, [1]),
    ({'c': 6}, []), ({'c': 2, 'i': 1, 'j': 1, 'k': 3}, [])
])
def test_index(index, labels, answer):
    result = index.indices(**labels)
    assert result == answer


@pytest.mark.parametrize('ind, answer', [
    (1, (2, 1, 0, 3)), (2, (2, 2, 0, 5)), (3, (4, 0, 0, 4)), (4, (4, 0, 0, 5)), 
    (0, (1, 1, 0, 3)), (6, (5, 1, 0, 3)), (5, (5, 0, 0, 4)), 
])
def test_label(index, ind, answer):
    result = index.label(ind)
    assert result == answer


def test_index_lenght(index):
    assert len(index) == 7


""" @pytest.mark.parametrize('axes, labels, sdata, answer', [
    (
        ('cell', 'i', 'j'), ((4, 2, 3, 1), (0, 1, 2), (0, 1)),
        {(1, 0, 0): 3, (1, 2, 0): 2, (2, 1, 1): 4, (3, 1, 0): 5, (4, 0, 0): 1},
        {(3, 0, 0): 3, (3, 2, 0): 2, (1, 1, 1): 4, (2, 1, 0): 5, (0, 0, 0): 1}
    )
])
def test_create(axes, labels, sdata, answer):
    sd = data.SparseData(axes, labels, sdata)
    assert sd.axes == axes
    assert sd.labels == labels
    for index, value in answer.items():
        assert sd.data[index] == value
    assert sd.data.nnz == len(answer)


@pytest.mark.parametrize('tensor1, tensor2, answer', [
    (
        (
            ('cell', 'i', 'j'), ([1, 2, 3, 4], [0, 1, 2], [0, 1]), 
            {(1, 0, 0): 3, (1, 2, 0): 2, (2, 1, 1): 4, (3, 1, 0): 5, (4, 0, 0): 1}
        ),
        (
            ('cell', 'cell'), ([1, 2, 3, 4], [1, 2, 3, 4]),  
            {(1, 1): 2, (2, 2): 0.5, (3, 3): 4, (4, 4): 0.1}
        ),
        (
            ('cell', 'i', 'j'), ((1, 2, 3, 4), (0, 1, 2), (0, 1)), 
            {(0, 0, 0): 6, (0, 2, 0): 4, (1, 1, 1): 2, (2, 1, 0): 20, (3, 0, 0): 0.1}
        )
    )
])
def test_tensor_dot(tensor1, tensor2, answer):
    t1 = data.SparseData(*tensor1)
    t2 = data.SparseData(*tensor2)
    result = t2.tensor_dot(t1)
    assert result.axes == answer[0]
    assert result.labels == answer[1]
    for index, value in answer[2].items():
        assert result.data[index] == value
    assert result.data.nnz == len(answer[2])


@pytest.mark.parametrize('tensor1, tensor2, answer', [
    (
        (
            ('cell', 'i', 'j'), ([1, 2, 3, 4], [0, 1, 2], [0, 1]), 
            {(1, 0, 0): 3, (1, 2, 0): 2, (2, 1, 1): 4, (3, 1, 0): 5, (4, 0, 0): 1}
        ),
        (
            ('i', 'j'), ([0, 1, 2], [0, 1]), 
            {(0, 0): 2, (2, 0): 3, (1, 0): 4}
        ),
        (
            ('cell', 'i', 'j'), ((1, 2, 3, 4), (0, 1, 2), (0, 1)), 
            {(0, 0, 0): 6, (0, 2, 0): 6, (2, 1, 0): 20, (3, 0, 0): 2}
        )
    ),
    (
        (
            ('i', 'cell', 'j'), ([0, 1, 2], [1, 2, 3, 4], [0, 1]), 
            {(0, 1, 0): 3, (2, 1, 0): 2, (1, 2, 1): 4, (1, 3, 0): 5, (0, 4, 0): 1}
        ),
        (
            ('i', 'j'), ([0, 1, 2], [0, 1]), 
            {(0, 0): 2, (2, 0): 3, (1, 0): 4}
        ),
        (
            ('cell', 'i', 'j'), ((1, 2, 3, 4), (0, 1, 2), (0, 1)), 
            {(0, 0, 0): 6, (0, 2, 0): 6, (2, 1, 0): 20, (3, 0, 0): 2}
        )
    )
])
def test_multiply(tensor1, tensor2, answer):
    t1 = data.SparseData(*tensor1)
    t2 = data.SparseData(*tensor2)
    result = t1.multiply(t2)
    assert result.axes == answer[0]
    assert result.labels == answer[1]
    for index, value in answer[2].items():
        assert result.data[index] == value
    assert result.data.nnz == len(answer[2])


@pytest.mark.parametrize('tensor, axeslabs, answer', [
    (
        (
            ('cell', 'i', 'j'), ([1, 2, 3, 4], [0, 1, 2], [0, 1]), 
            {(1, 0, 0): 3, (1, 2, 0): 2, (2, 1, 1): 4, (3, 1, 0): 5, (4, 0, 0): 1}
        ),
        {
            'i': ('xbins', [-1.0, 1.0, 3.0, 6.0]), 
            'j': ('ybins', [-5.0, 5.0, 10.0])
        },
        (
            ('cell', 'xbins', 'ybins'), ((1, 2, 3, 4), (-1.0, 1.0, 3.0, 6.0), 
            (-5.0, 5.0, 10.0)), 
            {(0, 0, 0): 3, (0, 2, 0): 2, (1, 1, 1): 4, (2, 1, 0): 5, (3, 0, 0): 1}
        )
    ),
    
])
def test_replace_axes(tensor, axeslabs, answer):
    t = data.SparseData(*tensor)
    result = t.replace_axes(**axeslabs)
    assert result.axes == answer[0]
    assert result.labels == answer[1]
    for index, value in answer[2].items():
        assert result.data[index] == value
    assert result.data.nnz == len(answer[2])
 """