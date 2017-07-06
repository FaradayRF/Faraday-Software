#!/usr/bin/python3

# Receiver code for Opus over FaradayRF

import sys
from base64 import b64decode

# For now all this does is base64 decode the input

while True:
    in_line = sys.stdin.buffer.readline()
    out_bytes = b64decode(in_line)
        
    sys.stdout.buffer.write(out_bytes)
    sys.stdout.buffer.flush()
