#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        /Applications/deviceconfiguration/deviceconfiguration.py
# Purpose:     Starts up device configuration application by calling the main() function
#              of the faraday.deviceconfiguration module
#
# Author:      Bryce Salmi
#
# Created:     6/28/2017
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import sys
import os

# Add Faraday library to the Python path.
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from faraday import deviceconfiguration

deviceconfiguration.main()
