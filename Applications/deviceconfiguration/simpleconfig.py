#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        /Applications/deviceconfiguration/simpleconfig.py
# Purpose:     Starts up simpleconfig by calling the main() function
#              of the faraday.simpleconfig module
#
# Author:      Bryce Salmi
#
# Created:     6/29/2017
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import sys
import os

# Add Faraday library to the Python path.
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from faraday import simpleconfig

simpleconfig.main()
