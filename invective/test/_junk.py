
"""
Useful things, but poorly maintained.  Things here need to have unit tests
written for them and to be moved to a sensible public location - most likely not
anywhere in invective.
"""

from os import devnull
from sys import executable
from subprocess import PIPE, Popen

from twisted.python.modules import getModule
from twisted.trial.unittest import SkipTest

from invective import __version__

# Copied out of twisted/scripts/test/test_scripts.py and then hacked a little
# bit to work with invective instead.
def outputFromPythonScript(script, *args):
    """
    Synchronously run a Python script, with the same Python interpreter that
    ran the process calling this function, using L{Popen}, using the given
    command-line arguments, with standard input and standard error both
    redirected to L{os.devnull}, and return its output as a string.

    @param script: The path to the script.
    @type script: L{FilePath}

    @param args: The command-line arguments to follow the script in its
        invocation (the desired C{sys.argv[1:]}).
    @type args: L{tuple} of L{str}

    @return: the output passed to the proces's C{stdout}, without any messages
        from C{stderr}.
    @rtype: L{bytes}
    """
    nullInput = file(devnull, "rb")
    nullError = file(devnull, "wb")
    stdout = Popen([executable, script.path] + list(args),
                   stdout=PIPE, stderr=nullError, stdin=nullInput).stdout.read()
    nullInput.close()
    nullError.close()
    return stdout



class ScriptTestsMixin:
    """
    Mixin for L{TestCase} subclasses which defines a helper function for testing
    a Twisted-using script.
    """
    bin = getModule("invective").pathEntry.filePath.child("bin")

    def scriptTest(self, name):
        """
        Verify that the given script runs and uses the version of Twisted
        currently being tested.

        This only works when running tests against a vcs checkout of Twisted,
        since it relies on the scripts being in the place they are kept in
        version control, and exercises their logic for finding the right version
        of Twisted to use in that situation.

        @param name: A path fragment, relative to the I{bin} directory of a
            Twisted source checkout, identifying a script to test.
        @type name: C{str}

        @raise SkipTest: if the script is not where it is expected to be.
        """
        script = self.bin.preauthChild(name)
        if not script.exists():
            raise SkipTest(
                "Script tests do not apply to installed configuration.")

        scriptVersion = outputFromPythonScript(script, '--version')

        self.assertIn(__version__, scriptVersion)
