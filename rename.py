#!/usr/bin/env python
# coding: utf-8

"""
Rename a string in CamelCase, snake_case and ALL_CAPS_CASE
in code and filenames in one go.
"""

__version__ = '0.1.1'
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

# whole word options
WHOLE_WORD = 2
ALLOW_UNDERSCORES = 1
ANY_SEQUENCE = 0

def is_binary(filename):
    """Return true if the given filename is binary.
    @raise EnvironmentError: if the file does not exist or cannot be accessed.
    @attention: found @ http://bytes.com/topic/python/answers/21222-determine-file-type-binary-text on 6/08/2010
    @author: Trent Mick <TrentM@ActiveState.com>
    @author: Jorge Orpinel <jorge@orpinel.com>"""
    fin = open(filename, 'rb')
    try:
        CHUNKSIZE = 1024
        while 1:
            chunk = fin.read(CHUNKSIZE)
            if '\0' in chunk: # found null byte
                return True
            if len(chunk) < CHUNKSIZE:
                break # done
    # A-wooo! Mira, python no necesita el "except:". Achis... Que listo es.
    finally:
        fin.close()

    return False

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


def edit_line(src, dest, line, word_option=ANY_SEQUENCE):
    """Rename in a single line of text.

    >>> edit_line('hello_world', 'whats_up', 'hi hello_world <3')
    'hi whats_up <3'
    >>> edit_line('hello_world', 'whats_up', 'hi HelloWorld HELLO_WORLD <3')
    'hi WhatsUp WHATS_UP <3'
    >>> edit_line('HelloWorld', 'WhatsUp', 'hi HelloWorld HELLO_WORLD <3')
    'hi WhatsUp WHATS_UP <3'
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

    src_snake = camel2snake(src)
    dest_snake = camel2snake(dest)
    src_camel = snake2camel(src)
    dest_camel = snake2camel(dest)
    src_all_caps = src_snake.upper()
    dest_all_caps = dest_snake.upper()

    # if not recognized as snake or camel, both transforms will leave its
    # input string intact

    recognized = src_snake != src_camel and dest_snake != dest_camel
    if not recognized:
        logging.debug('case not recognized, performing plain search/replace')
        return line.replace(src, dest)

    if word_option == ANY_SEQUENCE:
        line = line.replace(src_snake, dest_snake)
        line = line.replace(src_camel, dest_camel)
        return line.replace(src_all_caps, dest_all_caps)

    if word_option == WHOLE_WORD:
        template = r'\b{}\b'

        src_snake = template.format(src_snake)
        src_camel = template.format(src_camel)
        src_all_caps = template.format(src_all_caps)

        line = re.sub(src_snake, dest_snake, line)
        line = re.sub(src_camel, dest_camel, line)
        return re.sub(src_all_caps, dest_all_caps, line)

    if word_option == ALLOW_UNDERSCORES:
        src_template = r'(\b|(_+)){}((_+)|\b)'
        dest_template = r'\1{}\3'

        src_snake = src_template.format(src_snake)
        src_camel = src_template.format(src_camel)
        src_all_caps = src_template.format(src_all_caps)

        dest_snake = dest_template.format(dest_snake)
        dest_camel = dest_template.format(dest_camel)
        dest_all_caps = dest_template.format(dest_all_caps)

        logging.debug('underscore caps: {}->{}'.format(src_all_caps,
                      dest_all_caps))
        line = re.sub(src_snake, dest_snake, line)
        line = re.sub(src_camel, dest_camel, line)
        return re.sub(src_all_caps, dest_all_caps, line)


def edit_text(src, dest, text_lines, word_option=ANY_SEQUENCE):
    """Rename in lines of text."""

    return [edit_line(src, dest, line, word_option) for line in text_lines]


def process_file(src, dest, word_option, path,  # pylint: disable=R0913
                 diff, text_only):
    """Rename in a file."""

    if is_binary(path):
        return

    if not text_only:
        new_path = edit_line(src, dest, path, word_option)
    else:
        new_path = path

    try:
        with io.open(path, 'r', encoding='utf-8') as in_file:
            in_lines = in_file.readlines()
    except IOError as e:
        logging.warn('could not read file: {0}, error message: {1}'
                .format(path, e))
        return
    except UnicodeDecodeError as e:
        logging.debug('could not read file: {0}, error message: {1}'
                .format(path, e))
        return

    out_lines = list(edit_text(src, dest, in_lines, word_option))

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
            logging.warn('could not read file: {0}, error message: {1}'
                    .format(path, e))

        if new_path != path:
            try:
                shutil.copymode(path, new_path)
                os.unlink(path)
            except OSError as e:
                logging.warn('could not delete file: {0}, error message: {1}'
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
