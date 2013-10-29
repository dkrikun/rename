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
import argparse


def parse_cmdline_args():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description='Rename a string in CamelCase'
                                     ', snake_case and ALL_CAPS in one go')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__))
    parser.add_argument('-w', '--word', action='store_true',
                        help='force SOURCE to match only whole words')
    parser.add_argument('--almost-word', action='store_true',
                        help='like -w, but also allow for any number of '
                        'surrounding underscores')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='do not change anything, just show what it '
                        'would do')
    parser.add_argument('-d', '--diff', action='store_true',
                        help='shows diff instead of modifying files inplace')
    parser.add_argument('-f', '--text-only', action='store_true',
                        help='only perform search/replace in file contents, do'
                        'not rename any files')
    parser.add_argument('-a', '--ack', action='store_true',
                        help='if ack tool is installed, delegate searching '
                        'patterns to it')
    parser.add_argument('-V', '--verbose', action='store_true',
                        help='be verbose')
    parser.add_argument('-q', '--silent', action='store_true',
                        help='be silent')
    parser.add_argument('source', metavar='SOURCE', nargs=1,
                        help='source string to be renamed')
    parser.add_argument('dest', metavar='DEST', nargs=1,
                        help='string to replace with')
    parser.add_argument('patterns', metavar='PATTERN', nargs='+',
                        help='shell-like file name patterns to process')
    return parser.parse_args()


def main():
    """Main here."""

    args = parse_cmdline_args()
    severity_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(stream=sys.stderr, level=severity_level)
    logging.debug(args)


if __name__ == "__main__":
    sys.exit(main())
