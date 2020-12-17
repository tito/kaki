# -*- coding: utf-8 -*-

MAJOR = 0
MINOR = 1
PATCH = 5

RELEASE = False

__version__ = "%d.%d.%d" % (MAJOR, MINOR, PATCH)

__appname__ = "Kaki App"

if not RELEASE:
    __version__ += ".dev0"