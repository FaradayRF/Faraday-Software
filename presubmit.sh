#!/bin/sh

# Exit on first error.
set -e

# Run a limited set of PyFlakes tests through flake8.
flake8 --select=F --ignore=F821
