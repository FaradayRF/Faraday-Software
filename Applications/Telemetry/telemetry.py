#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        /Telemetry/telemetry.py
# Purpose:     Starts up Telemetry application by calling the main() function
#              of faraday.telemetry module.
#
# Author:      Bryce Salmi
#
# Created:     4/27/2017
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import sys
import os

# Add Faraday library to the Python path.
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from faraday import telemetry

telemetry.main()
