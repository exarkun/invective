# -*- test-case-name: invective.test.test_script -*-

"""
Primary command line hook.
"""

from errno import EEXIST
from os.path import expanduser

from twisted.python.filepath import FilePath
from twisted.python.usage import Options

from twisted.conch.stdio import runWithProtocol
from twisted.python.log import startLogging

from invective import __version__
from invective.tui import CommandLineUserInterface

class InvectOptions(Options):
    """
    L{InvectOptions} defines the command line interface to the I{invective}
    command.
    """
    optParameters = [
        ("logfile", None, expanduser("~/.invective/invective.log"),
         "Specify a file to which to write log messages"),
        ]

    def opt_version(self):
        """
        Display Invective version and exit.
        """
        print "Invective version:", __version__
        raise SystemExit(0)



class _InvectScript(object):
    """
    L{_InvectScript} implements the main function implementing the I{invective}
    command.
    """
    _startLogging = staticmethod(startLogging)
    _runWithProtocol = staticmethod(runWithProtocol)

    def main(self, argv):
        """
        Parse the command line arguments given by C{argv} and use the resulting
        configuration to launch the I{invective} application.

        @param argv: A C{sys.argv}-style array, excluding the conventional 0th
            element (the program name).
        @type argv: L{list} of L{bytes}

        @return: A L{Deferred} which fires when the application has completed.
        """
        options = InvectOptions()
        options.parseOptions(argv)
        return self.run(options)


    def run(self, options):
        """
        Run the I{invective} application based on the given configuration.

        @param options: Command-line specified arguments for how to behave.
        @type options: L{InvectOptions}

        @return: A L{Deferred} which fires when the application has completed.
        """
        parent = FilePath(options["logfile"]).parent()
        try:
            parent.makedirs()
        except EnvironmentError as e:
            if e.errno != EEXIST:
                raise

        with open(options["logfile"], "a") as logFile:
            self.startLogging(logFile)
        self._runWithProtocol(CommandLineUserInterface)


    def startLogging(self, fObj):
        """
        Add a log observer to the L{twisted.python.log} system which will write
        log events to the given file object.
        """
        # XXX This is lame.  I'd rather have a LogPublisher reference and just
        # call addObserver on it, but startLogging calls
        # startLoggingWithObserver which has a bunch of extra logic that's
        # pretty important.
        self._startLogging(fObj)


main = _InvectScript().main
