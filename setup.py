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

import os
from setuptools import setup

# serve README.txt from folder if queried for description
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "faraday",
    version = "0.0.1",
    author = "FaradayRF",
    author_email = "Support@FaradayRF.com",
    description = "FaradayRF open source software for the Faraday radio.",
    license = "GPLv3",
    keywords = "faraday radio faradayrf ham amateur",
    url = "https://www.FaradayRF.com",
    packages=['faraday', 'tests'],
    long_description=read('README'),
    classifiers=[
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
)