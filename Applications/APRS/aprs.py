#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        /Applications/APRS/aprs.py
# Purpose:     Starts up APRS application by calling the main() function
#              of the faraday.aprs module
#
# Author:      Bryce Salmi
#
# Created:     4/27/2017
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import sys
import os

# Add Faraday library to the Python path.
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from faraday import aprs

aprs.main()
