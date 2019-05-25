# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='r2s_rfda',
    version='0.1',
    packages=find_packages(),
    entry_points={'console_scripts': ['r2s_rfda = r2s_rfda.launcher:main']},
    author='Roman Rodionov',
    author_email='r.rodionov@iterrf.ru',
    package_data={'': ['templates/*.temp']}
)