#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Name:        /Applications/Data/data.py
# Purpose:      Provides a generic data server for Faraday through Proxy.
#
# Author:      Brent Salmi
#
# Created:     07/06/2017
# Licence:     GPLv3
#-------------------------------------------------------------------------------


import sys
import os

# Add Faraday library to the Python path.
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from faraday import data

data.main()
