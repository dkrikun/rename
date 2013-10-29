All hands to battle stations, rename at will!
======

[![Build Status](https://travis-ci.org/dkrikun/rename.png)](https://travis-ci.org/dkrikun/rename)

Rename a string in **CamelCase**, **snake_case** and **ALL_CAPS** in code and
filenames in one go.

### Example

Say you've got a cool `hex_clock.cpp`:


```cpp
#ifndef _HEX_CLOCK_H
#define _HEX_CLOCK_H

class HexClock
{
  // ... good stuff here
};

#endif
```

Cute! And now.. rename at will!

`rename.py hex_clock hacker_clock`

Meet the new shiny `hacker_clock.h`:

```cpp
#ifndef _HACKER_CLOCK_H
#define _HACKER_CLOCK_H


class HackerClock
{
  // ... good stuff here
};

#endif
```

### What it knows to do

**rename** is like a search/replace engine on steroids, it takes a string
to search for, converts it to all possible cases (**CamelCase**, **snake_case**
and **ALL_CAPS**), and performs a search/replace with the corresponding case
version of the destination string.

For example, `rename.py hex_clock hacker_clock` above, does the following
substitutions in text files:

   `hex_clock` --> `hacker_clock`  
   `HexClock` --> `HackerClock`  
   `HEX_CLOCK` --> `HACKER_CLOCK`  

Also, by default, the file `hex_clock.h` is renamed to `hacker_clock.h`, file
rename can be disabled with `-f` flag, see **Usage** below.

### Usage

```shell
usage: rename.py [-h] [--version] [-w] [--almost-word] [-n] [-d] [-f] [-a]
                 [-V] [-q]
                 SOURCE DEST PATTERN [PATTERN ...]

Rename a string in CamelCase, snake_case and ALL_CAPS in one go

positional arguments:
  SOURCE           source string to be renamed
  DEST             string to replace with
  PATTERN          shell-like file name patterns to process

optional arguments:
  -h, --help       show this help message and exit
  --version        show program's version number and exit
  -w, --word       force SOURCE to match only whole words
  --almost-word    like -w, but also allow for any number of surrounding
                   underscores
  -n, --dry-run    do not change anything, just show what it would do
  -d, --diff       shows diff instead of modifying files inplace
  -f, --text-only  only perform search/replace in file contents, donot rename
                   any files
  -a, --ack        if ack tool is installed, delegate searching patterns to it
  -V, --verbose    be verbose
  -q, --silent     be silent
```


### Dependencies

Python 2.7 will do.
