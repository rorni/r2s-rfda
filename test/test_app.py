# -*- coding: utf-8 -*-

import pytest
from pathlib import Path
import numpy as np

from r2s_rfda import launcher, fetch


@pytest.fixture(scope='module')
def full_calculations():
    path = Path('test/full2')
    if not (path / 'settings.cfg').exists():
        launcher.prepare_task(path, 'config.ini')
        launcher.run_task(path, 6)
    return path


@pytest.fixture(scope='module')
def simple_calculations():
    path = Path('test/simple2')
    if not (path / 'settings.cfg').exists():
        launcher.prepare_task(path, 'config.ini')
        launcher.run_task(path, 6)
    return path
       

@pytest.mark.parametrize('axes, labels, outdata', [
   (('time', 'g_erg', 'cell', 'xbins', 'ybins', 'zbins'),
    (
        (31558000, 31558600, 31562200, 31645000, 32422600, 63094600),
        (0, 0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.40, 0.60, 0.80, 1.00, 1.22,
          1.44, 1.66, 2.00, 2.50, 3.00, 4.00, 5.00, 6.50, 8.00, 10.00, 12.00,
          14.00, 20.00
        ),
        (2, 3, 4, 5, 6, 7),
        (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
         28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45,
         46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
         64, 65, 66, 67, 68, 69, 70),
        (-10, 10), (-10, 10)
    ),
    np.array([
        [4.9092e+09, 2.5711e+09, 2.2591e+09, 7.0520e+08],
        [2.7429e+09, 1.4365e+09, 1.2622e+09, 3.9401e+08],
        [1.8606e+09, 9.7446e+08, 9.1343e+08, 2.6728e+08],
        [1.4365e+09, 7.5232e+08, 6.6104e+08, 2.0635e+08],
        [1.1831e+09, 5.4445e+08, 6.1963e+08, 1.4933e+08],
        [9.7446e+08, 4.7838e+08, 4.2033e+08, 1.2300e+08],
        [8.0259e+08, 3.9401e+08, 3.4620e+08, 9.4957e+07],
        [8.0259e+08, 3.4620e+08, 3.0419e+08, 8.3435e+07],
        [9.7446e+08, 3.0419e+08, 2.6728e+08, 7.3311e+07],
        [1.3465e+09, 3.0419e+08, 2.6728e+08, 7.3311e+07],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [7.0520e+08, 1.2300e+08, 1.0807e+08, 2.7786e+07],
        [3.9401e+08, 8.9010e+07, 7.8209e+07, 2.0108e+07],
        [2.3485e+08, 6.4415e+07, 5.6599e+07, 1.3641e+07],
        [1.5931e+08, 4.9731e+07, 4.3697e+07, 1.1235e+07],
        [1.1529e+08, 4.3697e+07, 3.5990e+07, 9.2532e+06],
        [8.9010e+07, 3.3736e+07, 2.9642e+07, 7.1439e+06],
        [7.8209e+07, 2.9642e+07, 2.6045e+07, 6.2770e+06],
        [7.8209e+07, 2.6045e+07, 2.2885e+07, 5.5153e+06],
        [9.4957e+07, 2.4414e+07, 2.1452e+07, 4.8461e+06],
        [1.3998e+08, 2.7786e+07, 2.2885e+07, 5.8839e+06],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [6.8719e+07, 1.1235e+07, 9.8715e+06, 2.3791e+06],
        [3.8395e+07, 7.6212e+06, 6.6964e+06, 1.5128e+06],
        [2.2885e+07, 5.5153e+06, 4.8461e+06, 1.1679e+06],
        [1.4552e+07, 4.2581e+06, 3.7414e+06, 9.0169e+05],
        [1.0531e+07, 3.5071e+06, 2.8885e+06, 6.9614e+05],
        [8.1304e+06, 2.8885e+06, 2.5380e+06, 5.7336e+05],
        [7.1439e+06, 2.5380e+06, 2.2301e+06, 5.0379e+05],
        [6.6964e+06, 1.9595e+06, 1.7217e+06, 4.1493e+05],
        [8.1304e+06, 2.0904e+06, 1.7217e+06, 4.1493e+05],
        [1.1985e+07, 2.2301e+06, 1.9595e+06, 4.7223e+05],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00],
        [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00]
    ])
   )
])
def test_full_fetch(full_calculations, axes, labels, outdata):
    launcher.fetch_task(full_calculations)
    data = fetch.load_data(full_calculations, 'gamma')
    assert data.axes == axes
    assert data.labels == labels
    data_arr = data.data[-4:, :, :, :, 0, 0]
    for i in range(outdata.shape[0]):
        for j in range(outdata.shape[1]):
            arr = data_arr[j, :, :, i]
            val = arr.sum()
            if not (val / 400 == pytest.approx(outdata[i, j], 0.1)):
                print(i, j, val/400, outdata[i, j])

    assert False
            

def test_simple_fetch(full_calculations, simple_calculations):
    launcher.fetch_task(simple_calculations)
    launcher.fetch_task(full_calculations)
    beta = launcher.load_config(simple_calculations)['beta']
    alpha = launcher.load_config(simple_calculations)['alpha']
    simple = fetch.load_data(simple_calculations, 'atoms')
    full = fetch.load_data(full_calculations, 'atoms')
    assert simple.axes == full.axes
    # assert simple.labels == full.labels
    assert simple.data.shape == full.data.shape
    # assert simple.data.nnz == full.data.nnz
    cnt = 0
    cnt_c = 0
    print(full.labels)
    for index in zip(*simple.data.nonzero()):
        if simple.data[index] != pytest.approx(full.data[index], 1.e-4):
            print(index, simple.data[index], full.data[index], (simple.data[index] - full.data[index]) / full.data[index], beta.data[index[2:]])
            cnt += 1
        else:
            cnt_c += 1
    print(cnt, cnt_c, full.data.nnz)
    assert False


@pytest.mark.parametrize('results', [
    {
        2: (1.0000, range(0, 10)),
        3: (0.1282, range(10, 20)),
        4: (1.0000, range(20, 30)),
        5: (0.1282, range(30, 40)),
        6: (1.0000, range(40, 50)),
        7: (0.1282, range(50, 60))
    }
])
def test_beta(simple_calculations, results):
    beta = launcher.load_config(simple_calculations)['beta']
    # assert beta.data.nnz == 60
    for c, i, j, k in zip(*beta.data.nonzero()):
        cn = beta.labels[0][c]
        print(cn, i, j, k, beta.data[c, i, j, k])
        if i in results[cn][1]:
            assert beta.data[c, i, j, k] == pytest.approx(results[cn][0], 0.1)
        else:
            assert beta.data[c, i, j, k] < results[cn][0] * 1.e-1

