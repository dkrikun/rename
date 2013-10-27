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

Cute! And now.. rename at will! `rename.py hex_clock hacker_clock`

Then meed the new shiny `hacker_clock.h`:

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

**rename** is like a search/replace engine on steroids, it takes a string,
usually a class/variable name, converts it to all cases (CamelCase, snake_case
and ALL_CAPS), and replaces all matching occurances with the corresponding
destination strings.

For example, `rename.py hex_clock hacker_clock` above, does the following
substitutions:

   `hex_clock` --> `hacker_clock`
   `HexClock` --> `HackerClock`
   `HEX_CLOCK` --> `HACKER_CLOCK`

 - Surrounding underscores are preserved.
 - By default, rename does not consider word boundaries, i.e `HexClockTest`
 will become `HackerClockTest`, though it can be changed with `-w`.
 - By default, rename also performs rename of files and directories, this
 can be disabled by `-t` flag.
 - By default, the files are edited inplace, this can be altered with `-d`
 which prints the result to stdout.

### Dependencies

Python 2.7 will do.
