#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        /Applications/SimpleUI/simpleui.py
# Purpose:     Starts up the SimpleUI application by calling the main() function
#              of faraday.simpleui module.
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
from faraday import simpleui

simpleui.main()
