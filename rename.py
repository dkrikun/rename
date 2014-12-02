#!/usr/bin/env python
# coding: utf-8

"""
Rename a string in CamelCase, snake_case and ALL_CAPS_CASE
in code and filenames in one go.
"""

__version__ = '0.1.2'
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
import re

from binaryornot.check import is_binary

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
        if '.git' in dirs:
            dirs.remove('.git')     # do not visit .git

        if '.hg' in dirs:
            dirs.remove('.hg')      # do not visit .hg

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


def is_snake_case(id_name):
    """Check if id_name is written in snake case.

    Actually, it is restricted to a certain subset of snake case, so that
    we can guarantee camel->snake->camel roundtrip.

    >>> is_snake_case('')
    False
    >>> is_snake_case('_')
    False
    >>> is_snake_case('h')
    True
    >>> is_snake_case('hello_world')
    True
    >>> is_snake_case(' hello_world ')
    False
    >>> is_snake_case('_hello')
    False
    >>> is_snake_case('hello_')
    False
    >>> is_snake_case('__hello_world__')
    False
    >>> is_snake_case('_hello6_wor7d_')
    False
    >>> is_snake_case('hello6_wor7d')
    True
    >>> is_snake_case('hello__world')
    False
    >>> is_snake_case('hello-world')
    False
    >>> is_snake_case('HelloWorld')
    False
    >>> is_snake_case('ab6')
    True
    >>> is_snake_case('ab_6')
    False
    >>> is_snake_case('6_ab')
    False
    >>> is_snake_case('ab_6_ab6')
    False
    """

    snake_case_re = re.compile(r"""
            [a-z][a-z0-9]*      # first word is required, start w/ alpha
            (_[a-z][a-z0-9]*)*  # any number of words follow
            $
            """, re.VERBOSE)

    return snake_case_re.match(id_name) is not None


def is_camel_case(id_name):
    """Check if id_name is written in camel case.

    >>> is_camel_case('')
    False
    >>> is_camel_case('_')
    False
    >>> is_camel_case('h')
    False
    >>> is_camel_case('H')
    True
    >>> is_camel_case('HW')
    False
    >>> is_camel_case('hW')
    False
    >>> is_camel_case('hWW')
    False
    >>> is_camel_case('WhWhWhW')
    True
    >>> is_camel_case('HelloWorld')
    True
    >>> is_camel_case('helloWorld')
    False
    >>> is_camel_case('HWorld')
    False
    >>> is_camel_case('Hello6orld')
    True
    >>> is_camel_case('hello_world')
    False
    >>> is_camel_case('_Hello')
    False
    >>> is_camel_case('Hello_')
    False
    >>> is_camel_case('hello-world')
    False
    >>> is_camel_case('HelloWorld')
    True
    >>> is_camel_case('HelloGoodWorld77')
    True
    """

    camel_case_re = re.compile(r"""
            ([A-Z](?![A-Z])[a-z0-9]*)+    # neg lookahead is to exclude
                                          # e.g HWorld
            $
            """, re.VERBOSE)

    return camel_case_re.match(id_name) is not None


def is_lower_camel_case(id_name):
    """Check if id_name is written in camel case.

    >>> is_lower_camel_case('')
    False
    >>> is_lower_camel_case('_')
    False
    >>> is_lower_camel_case('H')
    False
    >>> is_lower_camel_case('h')
    True
    >>> is_lower_camel_case('hW')
    True
    >>> is_lower_camel_case('HW')
    False
    >>> is_lower_camel_case('HWW')
    False
    >>> is_lower_camel_case('hWhWhWh')
    True
    >>> is_lower_camel_case('helloWorld')
    True
    >>> is_lower_camel_case('HelloWorld')
    False
    >>> is_lower_camel_case('hWorld')
    True
    >>> is_lower_camel_case('hello6orld')
    True
    >>> is_lower_camel_case('hello_world')
    False
    >>> is_lower_camel_case('_hello')
    False
    >>> is_lower_camel_case('hello_')
    False
    >>> is_lower_camel_case('hello-world')
    False
    >>> is_lower_camel_case('helloGoodWorld77')
    True
    """

    lower_camel_case_re = re.compile(r"""
            [a-z]([A-Z]?[a-z0-9]*)*

            $
            """, re.VERBOSE)

    return lower_camel_case_re.match(id_name) is not None


def snake2camel(id_name):
    """Change id_name from snake to camel, provided it is in snake case,
    or else return id_name intact.

    >>> snake2camel('hello_world')
    'HelloWorld'
    >>> snake2camel('HelloWorld')
    'HelloWorld'
    >>> snake2camel('hello9')
    'Hello9'
    >>> snake2camel('hello9world')
    'Hello9world'
    >>> snake2camel('hello9_world')
    'Hello9World'
    >>> snake2camel('h')
    'H'
    >>> snake2camel('hw')
    'Hw'
    >>> snake2camel('hello_good_world77')
    'HelloGoodWorld77'
    """

    if not is_snake_case(id_name):
        return id_name

    word_start = re.compile(r'(\A|_)[a-z]')
    return word_start.sub(lambda x: x.group().lstrip('_').upper(), id_name)


def camel2snake(id_name):
    """Change id_name from camel to snake, provided it is in camel case,
    or else return id_name intact.

    >>> camel2snake('HelloWorld')
    'hello_world'
    >>> camel2snake('hello_world')
    'hello_world'
    >>> camel2snake('Hello8orld')
    'hello8orld'
    >>> camel2snake('H')
    'h'
    >>> camel2snake('Hw')
    'hw'
    >>> camel2snake('HelloGoodWorld77')
    'hello_good_world77'
    """

    if not is_camel_case(id_name):
        return id_name

    word_start = re.compile(r'[A-Z]')
    almost_ready = word_start.sub(lambda x: '_' + x.group().lower(), id_name)
    return almost_ready.lstrip('_')


def snake2lowercamel(id_name):
    """Change id_name from snake to lower camel case,
    provided it is in snake case, or else return id_name intact.

    >>> snake2lowercamel('')
    ''
    >>> snake2lowercamel('hello_world')
    'helloWorld'
    >>> snake2lowercamel('HelloWorld')
    'HelloWorld'
    >>> snake2lowercamel('hello9')
    'hello9'
    >>> snake2lowercamel('hello9world')
    'hello9world'
    >>> snake2lowercamel('hello9_world')
    'hello9World'
    >>> snake2lowercamel('h')
    'h'
    >>> snake2lowercamel('hw')
    'hw'
    >>> snake2lowercamel('hello_good_world77')
    'helloGoodWorld77'
    """

    if not is_snake_case(id_name):
        return id_name

    # Almost camel case, but lowercase the first letter
    camel = snake2camel(id_name)
    return camel[0].lower() + camel[1:]


def lowercamel2snake(id_name):
    """Change id_name from lower camel to snake,
    provided it is in lower camel case, or else return id_name intact.

    >>> lowercamel2snake('helloWorld')
    'hello_world'
    >>> lowercamel2snake('hello_world')
    'hello_world'
    >>> lowercamel2snake('hello8orld')
    'hello8orld'
    >>> lowercamel2snake('h')
    'h'
    >>> lowercamel2snake('hW')
    'h_w'
    >>> lowercamel2snake('helloGoodWorld77')
    'hello_good_world77'
    """

    if not is_lower_camel_case(id_name):
        return id_name

    word_start = re.compile(r'[A-Z]')
    almost_ready = word_start.sub(lambda x: '_' + x.group().lower(), id_name)
    return almost_ready.lstrip('_')


def upper2lowercamel(id_name):
    """Change id_name from upper to lower camel case,
    provided it is in upper camel case, or return id_name intact.

    >>> upper2lowercamel('')
    ''
    >>> upper2lowercamel('H')
    'h'
    >>> upper2lowercamel('HelloWorld')
    'helloWorld'
    """
    if not is_camel_case(id_name):
        return id_name

    return id_name[0].lower() + id_name[1:]


def lower2uppercamel(id_name):
    """Change id_name from upper to lower camel case,
    provided it is in upper camel case, or return id_name intact.

    >>> lower2uppercamel('')
    ''
    >>> lower2uppercamel('h')
    'H'
    >>> lower2uppercamel('helloWorld')
    'HelloWorld'
    """
    if not is_lower_camel_case(id_name):
        return id_name

    return id_name[0].upper() + id_name[1:]


def edit_line(src, dest, line, word_option=ANY_SEQUENCE):
    """Rename in a single line of text.

    >>> edit_line('HlWorld', 'WhatsUp', 'hi HlWorld hlWorld HL_WORLD <3')
    'hi WhatsUp whatsUp WHATS_UP <3'
    >>> edit_line('hello_world', 'whats_up', 'hi hello_world <3')
    'hi whats_up <3'
    >>> edit_line('hello_world', 'whats_up', 'hi hello_world <3')
    'hi whats_up <3'
    >>> edit_line('hl_world', 'whats_up', 'hi HlWorld hlWorld HL_WORLD <3')
    'hi WhatsUp whatsUp WHATS_UP <3'
    >>> edit_line('hlWorld', 'whatsUp', 'hi HlWorld hlWorld HL_WORLD <3')
    'hi WhatsUp whatsUp WHATS_UP <3'
    >>> edit_line('hello__world', 'WhatsUp', 'hi hello__world HELLO_WORLD <3')
    'hi WhatsUp HELLO_WORLD <3'
    >>> edit_line('hello_world', 'whats_up', 'hi hello_world <3', WHOLE_WORD)
    'hi whats_up <3'
    >>> edit_line('hl_wrld', 'whats_up', 'hiRhl_wrldR<3', ANY_SEQUENCE)
    'hiRwhats_upR<3'
    >>> edit_line('hl_wrld', 'whats_up', 'hiRhl_wrldR<3', WHOLE_WORD)
    'hiRhl_wrldR<3'
    >>> edit_line('hl_wrld', 'whats_up', 'hiRhl_wrldR<3', ALLOW_UNDERSCORES)
    'hiRhl_wrldR<3'
    >>> edit_line('hl_wrld', 'whats_up', '___hl_wrld__', ANY_SEQUENCE)
    '___whats_up__'
    >>> edit_line('hl_wrld', 'whats_up', '___hl_wrld__', ALLOW_UNDERSCORES)
    '___whats_up__'
    >>> edit_line('hl_wrld', 'whats_up', '___hl_wrld__', WHOLE_WORD)
    '___hl_wrld__'
    >>> edit_line('hl_wrld', 'whats_up', '___HlWrld__', ALLOW_UNDERSCORES)
    '___WhatsUp__'
    >>> edit_line('hex_clck', 'hacker_clck', '_HEX_CLCK_H', ALLOW_UNDERSCORES)
    '_HACKER_CLCK_H'
    """
    src_lowercamel = src_camel = src_snake = src
    dest_lowercamel = dest_camel = dest_snake = dest

    recognized = True

    if is_snake_case(src) and is_snake_case(dest):
        src_lowercamel, dest_lowercamel = map(snake2lowercamel, (src, dest))
        src_camel, dest_camel = map(snake2camel, (src, dest))

    elif is_lower_camel_case(src) and is_lower_camel_case(dest):
        src_snake, dest_snake = map(lowercamel2snake, (src, dest))
        src_camel, dest_camel = map(lower2uppercamel, (src, dest))

    elif is_camel_case(src) and is_camel_case(dest):
        src_snake, dest_snake = map(camel2snake, (src, dest))
        src_lowercamel, dest_lowercamel = map(upper2lowercamel, (src, dest))

    else:
        recognized = False

    src_all_caps = src_snake.upper()
    dest_all_caps = dest_snake.upper()

    if not recognized:
        logging.debug('case not recognized, performing plain search/replace')
        return line.replace(src, dest)

    subst_pairs = (
        (src_snake, dest_snake),
        (src_camel, dest_camel),
        (src_lowercamel, dest_lowercamel),
        (src_all_caps, dest_all_caps),
    )

    if word_option == ANY_SEQUENCE:
        for _src, _dest in subst_pairs:
            line = line.replace(_src, _dest)
        return line

    if word_option == WHOLE_WORD:
        template = r'\b{}\b'

        pairs = [(template.format(_src), _dest) for _src, _dest in subst_pairs]
        for _src, _dest in pairs:
            line = re.sub(_src, _dest, line)
        return line

    if word_option == ALLOW_UNDERSCORES:
        src_template = r'(\b|(_+)){}((_+)|\b)'
        dest_template = r'\1{}\3'

        pairs = [(src_template.format(_src), dest_template.format(_dest))
                 for _src, _dest in subst_pairs]

        for _src, _dest in pairs:
            line = re.sub(_src, _dest, line)
        return line


def edit_text(src, dest, text_lines, word_option=ANY_SEQUENCE):
    """Rename in lines of text."""

    return [edit_line(src, dest, line, word_option) for line in text_lines]


def process_file(src, dest, word_option, path,  # pylint: disable=R0913
                 diff, text_only):
    """Rename in a file."""

    if is_binary(path):
        return

    # if --text-only requested, do not perform substitutions in filepath
    if not text_only:
        new_path = edit_line(src, dest, path, word_option)
    else:
        new_path = path

    try:
        with io.open(path, 'r', encoding='utf-8') as in_file:
            in_lines = in_file.readlines()
    except IOError as e:
        logging.warn('could not read file, error message: {1}'
                .format(path, e))
        return
    except UnicodeDecodeError as e:
        logging.debug('could not read file, error message: {1}'
                .format(path, e))
        return

    # perform substitions in file contents
    out_lines = list(edit_text(src, dest, in_lines, word_option))

    # only output diff to stdout, do not write anything to file (if requested
    # by --diff)
    if diff:
        diffs = difflib.unified_diff(in_lines, out_lines,
                                     fromfile=path, tofile=new_path)
        for line in diffs:
            sys.stdout.write(line)
    else:
        try:
            with io.open(new_path, 'w', encoding='utf-8') as out_file:
                out_file.writelines(out_lines)
        except IOError as e:
            logging.warn('could not write file, error message: {1}'
                    .format(path, e))

        if new_path != path:
            try:
                shutil.copymode(path, new_path)
                os.unlink(path)
            except OSError as e:
                logging.warn('could not delete file, error message: {1}'
                        .format(path,e))
                return


def main():
    """Main here."""

    args = parse_cmdline_args()
    severity_level = logging.DEBUG if args.verbose else logging.WARNING
    if args.silent:
        severity_level = logging.CRITICAL
    logging.basicConfig(stream=sys.stderr, level=severity_level,
            format='%(message)s')
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
