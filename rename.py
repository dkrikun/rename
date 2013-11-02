#!/usr/bin/env python
# coding: utf-8

"""
Rename a string in CamelCase, snake_case and ALL_CAPS_CASE
in code and filenames in one go.
"""

__version__ = '0.1.0'
__author__ = 'Daniel Krikun'
__license__ = 'MIT'

import sys
import logging
import argparse
import os
import fnmatch
import io
import difflib
import shutil

# whole word options
WHOLE_WORD = 2
ALLOW_UNDERSCORES = 1
ANY_SEQUENCE = 0


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
    parser.add_argument('-d', '--diff', action='store_true',
                        help='shows diff instead of modifying files inplace')
    parser.add_argument('-f', '--text-only', action='store_true',
                        help='only perform search/replace in file contents, do'
                        'not rename any files')
    parser.add_argument('-a', '--ack', action='store_true',
                        help='if ack tool is installed, delegate searching '
                        'patterns to it')
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument('-V', '--verbose', action='store_true',
                                 help='be verbose')
    verbosity_group.add_argument('-q', '--silent', action='store_true',
                                 help='be silent')
    parser.add_argument('source', metavar='SOURCE',
                        help='source string to be renamed')
    parser.add_argument('dest', metavar='DEST',
                        help='string to replace with')
    parser.add_argument('patterns', metavar='PATTERN', nargs='+',
                        help='shell-like file name patterns to process')
    return parser.parse_args()


def edit_line(src, dest, word_option, line):
    """Rename in a single line of text."""

    return line.replace(src, dest)


def edit_text(src, dest, word_option, text_lines):
    """Rename in lines of text."""

    return [edit_line(src, dest, word_option, line) for line in text_lines]


def process_file(src, dest, word_option, path, diff, text_only):
    """Rename in a file."""

    if not text_only:
        new_path = edit_line(src, dest, word_option, path)
    else:
        new_path = path

    with io.open(path, 'r', encoding='utf-8') as in_file:
        in_lines = in_file.readlines()

    out_lines = list(edit_text(src, dest, word_option, in_lines))

    if diff:
        diffs = difflib.unified_diff(in_lines, out_lines,
                                     fromfile=path, tofile=new_path)
        for line in diffs:
            sys.stdout.write(line)
    else:
        with io.open(new_path, 'w', encoding='utf-8') as out_file:
            out_file.writelines(out_lines)
        if new_path != path:
            shutil.copymode(path, new_path)
            os.unlink(path)


def main():
    """Main here."""

    args = parse_cmdline_args()
    severity_level = logging.DEBUG if args.verbose else logging.WARNING
    if args.silent:
        severity_level = logging.CRITICAL
    logging.basicConfig(stream=sys.stderr, level=severity_level)
    logging.debug(args)

    word_option = ANY_SEQUENCE
    if args.word:
        word_option = WHOLE_WORD
    elif args.almost_word:
        word_option = ALLOW_UNDERSCORES

    pathes = get_paths(args.patterns, start_dir=None, max_depth=None)
    for path in pathes:
        logging.debug('renaming in {}'.format(path))

        process_file(args.source, args.dest, word_option, path,
                     args.diff, args.text_only)


if __name__ == "__main__":
    sys.exit(main())
