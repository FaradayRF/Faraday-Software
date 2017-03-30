#!/bin/sh

# Exit on first error.
set -e

# Run PyFlakes tests through flake8.
flake8 --select=F
