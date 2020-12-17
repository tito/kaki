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
    """ A set of logger for Kaki
    =============================

    - kaki_spacer()

            Empty spacer from kaki when logging is to dense and hard to read.
    
    - kaki_start()
    
            A logger when Kaki loaded it will return Kaki version, OS environmet and Bits as a result.

    - watch_kv()

            Passing one args from KV FILES and will return as populated sorted list of user kv files.

    - watch_kv_classes()

            Passing one args from CLASSES and will return as reversed populated sorted list of user classes.
    """
    # RESERVED




    # kaki spacer logger
    def kaki_spacer(result=None):
        """ who knows """

        result = Logger.info("{}:".format(__appname__))
        
        return result


    # kaki start logger
    def kaki_start(result=None):

        result = __appname__
        fversion = str(__version__)

        if result is not None:

            result = Logger.info("{}: {} activated on {} {}".format(result, "v"+fversion, OPERATING_SYSTEM, BITS_AND_ARCHITECTURE[0]))

            KakiLogger.kaki_spacer()

            return result

        else:
            result = Logger.error("{}: None type returned. Module doesn't exists...".format(result))

            return result


    # kaki watch kv files
    def watch_kv(*args):

        if args is not None:

            watch_kv = sorted(args)

            for kv in watch_kv:

                kvlist = sorted(kv)

                KakiLogger.kaki_spacer()

                # give user information what is their root kv file
                Logger.info("{}: Your root KV_FILES: {}".format(__appname__, kvlist[0]))

                KakiLogger.kaki_spacer()

                # block start of kv files list
                Logger.info("{}: v ------------------------ Start of your kv files ------------------------ v".format(__appname__))

                KakiLogger.kaki_spacer()

                for kv_file in kvlist:

                    # populate the log
                    Logger.info("{}: Watchin file: {}".format(__appname__, kv_file))

                KakiLogger.kaki_spacer()

                # block end of kv files list
                Logger.info("{}: ^ ------------------------  End of your kv files  ------------------------ ^".format(__appname__))

        else:
            Logger.error("{}: None type returned. check your KV_FILES".format(__appname__))


    # kaki watch kv classes
    def watch_kv_classes(*args):

        if args is not None:

            watch_classes = sorted(args)

            for kv_classes in watch_classes:

                kv_class = sorted(kv_classes)
                kv_class.reverse()

                KakiLogger.kaki_spacer()

                # give user information what is their root kv class
                Logger.info("{}: Your root CLASSES: {}".format(__appname__, kv_class[0]))

                KakiLogger.kaki_spacer()

                # block start of kv class list
                Logger.info("{}: v ------------------------ Start of your kv class ------------------------ v".format(__appname__))

                KakiLogger.kaki_spacer()

                for class_list in kv_class:

                    # populate the log
                    Logger.info("{}: Class: {}".format(__appname__, class_list))

                KakiLogger.kaki_spacer()

                # block end of kv class list
                Logger.info("{}: ^ ------------------------  End of your kv class  ------------------------ ^".format(__appname__))

        else:
            Logger.error("{}: None type returned. check your CLASSES".format(__appname__))