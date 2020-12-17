# -*- coding: utf-8 -*-
"""
syslog.py
==========
A set of functions for Kaki App configs logger.
"""
import platform

from kivy.logger import Logger

from kaki import __appname__, __version__




""" Sets of platform """

# bits and architecture information
BITS_AND_ARCHITECTURE = platform.architecture()
""" Will return as a tuple. ('Bit', 'Architecture) """


# processor information
CHECK_PROCESSOR = platform.processor()
""" To check original processor name """


# python version information
PY_VER = platform.python_version()
""" Checking python version """


# python compiler information
PY_COMPILER = platform.python_compiler()
""" This one will return:
<compiler> <version> <bits> and <processor-acrchitecture> """


# check operating system information
OPERATING_SYSTEM = platform.system()
""" checking operating system,
such as Linux, Darwin, Java, Windows """




# kaki logger main class
class KakiLogger:
    """ A set of logger for Kaki app
    =============================
    - kaki_start()

        A logger when Kaki loaded. Will return Kaki version, OS environmet and Bits.
    """
    # 


    # kaki start logger
    def kaki_start(result=None):

        result = __appname__
        fversion = str(__version__)

        if result is not None:

            result = Logger.info("%s: %s activated on %s %s" % (result, "v"+fversion, OPERATING_SYSTEM, BITS_AND_ARCHITECTURE[0]))

            return result

        else:
            result = Logger.error("%s: Module does't exists..." % result)

            return result