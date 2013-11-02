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
import os
import fnmatch


# copied from massedit.py by Jérôme Lecomte
def get_paths(patterns, start_dir=None, max_depth=1):
    """Retrieve files that match any of the patterns."""

    # Shortcut: if there is only one pattern, make sure we process just that.
    if len(patterns) == 1 and not start_dir:
        pattern = patterns[0]
        directory = os.path.dirname(pattern)
        if directory:
            patterns = [os.path.basename(pattern)]
            start_dir = directory
            max_depth = 1

    if not start_dir:
        start_dir = os.getcwd()
    for root, dirs, files in os.walk(start_dir):  # pylint: disable=W0612
        if max_depth is not None:
            relpath = os.path.relpath(root, start=start_dir)
            depth = len(relpath.split(os.sep))
            if depth > max_depth:
                continue
        names = []
        for pattern in patterns:
            names += fnmatch.filter(files, pattern)
        for name in names:
            path = os.path.join(root, name)
            yield path


def parse_cmdline_args():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description='Rename a string in CamelCase'
                                     ', snake_case and ALL_CAPS in one go')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__))
    word_group = parser.add_mutually_exclusive_group()
    word_group.add_argument('-w', '--word', action='store_true',
                            help='force SOURCE to match only whole words')
    word_group.add_argument('--almost-word', action='store_true',
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
    if args.silent:
        severity_level = logging.CRITICAL
    logging.basicConfig(stream=sys.stderr, level=severity_level)

    pathes = get_paths(args.patterns, start_dir=None, max_depth=None)
    for path in pathes:
        logging.debug('renaming in {}'.format(path))


if __name__ == "__main__":
    sys.exit(main())
