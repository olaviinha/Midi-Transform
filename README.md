midi-transform
============

Transform MIDI files using Python. Uses [python-midi](https://github.com/vishnubob/python-midi) to handle midi files.


Download
===========

* [Precompiled for Windows](https://docs.google.com/file/d/0B3A4M1pvdmsGRDB3NVBmbTR5WEE)


Instructions
===========
```
Usage: python2 midi-transform.py [input file] [output file]
Options:
  -l      , --log=<arg>                Write log to files.
  -i      , --invert                   Invert notes on pentagram.
  -r      , --reverse                  Reverse midi file.
  -c <arg>, --change_pitch=<arg>       Change pitch of midi file. Argument is pitch change. E.g: -c 2.
  -h        --help                     Print usage and exit.
```


Requires
===========

* [Python](http://www.python.org/download/) (2.6 or 2.7)
* [PySide](http://qt-project.org/wiki/PySide) For the GUI version.
* [PyGame](http://pygame.org) For the GUI version.

License
===========
midi-transform is released into the public domain by the copyright holders.