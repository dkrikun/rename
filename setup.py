#!/usr/bin/env python
# coding: utf-8


from setuptools import setup

import rename

requirements = [
    'binaryornot>=0.3.0',
]

setup(
    name='rename',
    version=rename.__version__,
    author=rename.__author__,
    author_email='krikun.daniel@gmail.com',
    url='https://github.com/dkrikun/rename/',
    license=rename.__license__,
    zip_safe=False,
    description='Rename a string in CamelCase, snake_case and ALL_CAPS in code and filenames in one go.',
    long_description=open('README.md').read(),
    scripts=['rename.py'],
    install_requires=requirements,
)
