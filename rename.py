#!/usr/bin/env python
# coding: utf-8

"""
Rename a string in CamelCase, snake_case and ALL_CAPS_CASE
in code and filenames in one go.
"""

__version__ = 0.10
__author__ = 'Daniel Krikun'
__license__ = 'MIT'

import sys
import logging


def main():
    """Main here."""
    logging.info('Rename at your command')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
