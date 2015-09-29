#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

setup(
    name='planetaryimage',
    version='0.3.0',
    description="Planetary image parser",
    long_description=readme + '\n\n' + history,
    author="PlanetaryPy Developers",
    author_email='contact@planetarypy.com',
    url='https://github.com/planetarypy/planetaryimage',
    packages=[
        'planetaryimage',
    ],
    package_dir={'planetaryimage':
                 'planetaryimage'},
    include_package_data=True,
    install_requires=[
        'numpy',
        'pvl',
        'six'
    ],
    license="BSD",
    zip_safe=False,
    keywords='planetaryimage',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
