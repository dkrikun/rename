All hands to battle stations, rename at will!
======

Rename a string in **CamelCase**, **snake_case** and **ALL_CAPS_CASE** in code and filenames in one go.

### Example

Say you've got cool `hex_clock.cpp`:


```cpp
#ifndef _HEX_CLOCK_H
#define _HEX_CLOCK_H

class HexClock
{
  // ... good stuff here
};

#endif
```

Cute! And now, rename at will: `rename.py hex_clock hacker_clock`

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

### Dependencies

Python 2.7 will do.
