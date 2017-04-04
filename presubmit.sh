#!/bin/sh

# Exit on first error.
set -e

# Run flake8 to check coding style and consistency.
flake8 --ignore=E116,E123,E124,E126,E127,E128,E201,E202,E203,E211,E221,E222,E225,E226,E227,E228,E231,E251,E261,E262,E265,E266,E402,E501
