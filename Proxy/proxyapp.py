#!/usr/bin/env python

import sys
import os
# Add Faraday library to the Python path.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from faraday.proxy import proxy

proxy.main()
