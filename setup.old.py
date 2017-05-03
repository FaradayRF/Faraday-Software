#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        /setup.py
# Purpose:     Python setuptools setup.py file contains all information necessary
#              to install faraday software with pip
#
# Author:      Bryce Salmi
#
# Created:     4/30/2017
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import setuptools


setuptools.setup(
    name = "faraday",
    version = "0.0.1a7",
    author = "FaradayRF",
    author_email = "Support@FaradayRF.com",
    description = "FaradayRF amateur radio open source software",
    license = "GPLv3",
    keywords = "faraday radio faradayrf ham amateur",
    url = "https://github.com/FaradayRF/Faraday-Software",
    packages = ['faraday','proxy'],
    long_description = "FaradayRF software",
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: Flask",
        "Framework :: Pytest",
        "Framework :: Flake8",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Topic :: Scientific/Engineering",
        "Topic :: Communications :: Ham Radio",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    install_requires = ['appdirs',
                        'click',
                        'configparser',
                        'enum34',
                        'flake8',
                        'Flask',
                        'Flask-Cors',
                        'itsdangerous',
                        'Jinja2',
                        'MarkupSafe',
                        'mccabe',
                        'packaging',
                        'py',
                        'pycodestyle',
                        'pyflakes',
                        'pyparsing',
                        'pyserial',
                        'pytest',
                        'pytest-flake8',
                        'requests',
                        'six',
                        'Werkzeug'],
)