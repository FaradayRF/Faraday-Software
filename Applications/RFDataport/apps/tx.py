#!/usr/bin/python3

# Transmitter code for Opus over FaradayRF

import sys
from base64 import b64encode

# For now all this does is base64 encode the input

while True:
    # Get the exact number of bytes expected from the encoder
    bytes_in = sys.stdin.buffer.read(32)

    out_line = b64encode(bytes_in)
    sys.stdout.buffer.write(out_line)
    sys.stdout.buffer.write(b"\n")
    sys.stdout.buffer.flush()

