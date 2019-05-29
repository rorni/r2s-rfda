# -*- coding: utf-8 -*-

import pytest
from pathlib import Path
import shutil

from r2s_rfda import utils


root = Path(__file__).resolve().parent


@pytest.mark.parametrize('folder, config', [
    ('test1', {
        'approach': 'full', 'task_list': [('folder1', ['task1', 'task2']), 
        ('folder2', ['task1', 'task2', 'task3'])], 'cells': [1, 3, 4, 5, 8],
        'materials': [2, 100, 400]
    })
])
def test_config(folder, config):
    path = root / folder
    path.mkdir()

    utils.save_config(path, **config)

    load_conf = utils.load_config(path)
    assert load_conf == config
    shutil.rmtree(path)
