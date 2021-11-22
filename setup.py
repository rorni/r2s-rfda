#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='r2s_rfda',
    version='0.4',
    packages=find_packages(),
    install_requires=[
        'sparse',
        'pypact',
        'mckit==0.1.2',
        'numpy'
    ],
    test_requires=[
        'pytest',
    ],
    dependency_links=['git+ssh://git@github.com/rorni/mckit.git#egg=mckit-0.1.2'],
    entry_points={'console_scripts': ['r2s-rfda = r2s_rfda.launcher:main']},
    author='Roman Rodionov',
    author_email='r.rodionov@iterrf.ru',
    package_data={'': ['templates/*.temp']}
)
