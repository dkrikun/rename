All hands to battle stations, rename at will!
======

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
Usage: rename.py SOURCE DEST [FILES OR DIRECTORIES]


-w, --word                  Force SOURCE to match only whole words
--almost-word               Like -w, but also allow for any number of surrounding `_`
-n, --dry-run               Do not rename anything, just show what it would do
-c [CASES], --case=[CASES]  Replace only the specified cases, valid values are:
                            `n` - none,
                            `s` - snake,
                            `c` - camel,
                            `a` - all caps.
                            Can be combined, for example `--case=cs`. If `none` is
                            specified, performs simple search/replace without case
                            conversions.
                            Default is `--case=sca`.
-d, --diff                  Shows diff instead of modifying files inplace.
-f, --text-only             Only perform search/replace in file contents, do not rename
                            files/directories.
--ack                       If ack tool is installed, delegate searching patterns to it.
-V, --verbose               Be verbose
-q, --silent                Be silent
--version                   Display version and exit
-h, --help                  Display this help and exit
```

### Dependencies

Python 2.7 will do.
