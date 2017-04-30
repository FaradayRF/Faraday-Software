#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Name:        /Applications/Hermes/hermesflaskserver.py
# Purpose:      Starts up the hermesflaskserver python module
#
# Author:      Bryce Salmi
#
# Created:     04/27/2017
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import sys
import os

# Add Faraday library to the Python path.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from faraday import hermesflaskserver

hermesflaskserver.main()
