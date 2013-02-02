
"""
Tests for L{invective.scripts.invect}.
"""

from errno import ENOTDIR
from os.path import expanduser

from twisted.python.filepath import FilePath
from twisted.trial.unittest import SynchronousTestCase

from invective.scripts.invect import InvectOptions, _InvectScript
from invective.test._junk import ScriptTestsMixin


class InvectOptionsTests(SynchronousTestCase):
    """
    Tests for L{InvectOptions}.
    """
    def parse(self, argv):
        """
        Create a new L{InvectOptions}, parse C{argv} using it, and then return
        it.
        """
        options = InvectOptions()
        options.parseOptions(argv)
        return options


    def test_logfile(self):
        """
        The I{logfile} option specifies to what file invective will log.
        """
        logfile = self.mktemp()
        options = self.parse(["--logfile", logfile])
        self.assertEqual(logfile, options["logfile"])


    def test_defaultLogfile(self):
        """
        The default log file is a path relative to the user's home directory.
        """
        options = self.parse([])
        self.assertEqual(
            expanduser("~/.invective/invective.log"), options["logfile"])



class InvectScriptTests(SynchronousTestCase):
    """
    Tests for L{_InvectScript}.
    """
    def spy(self, results):
        def spy(obj):
            results.append(obj)
        return spy

    def setUp(self):
        # Create an instance of the script to use in test methods
        self.script = _InvectScript()

        # Prevent it from actually running
        self.runs = []
        self.script._runWithProtocol = self.spy(self.runs)

        # And create a dictionary with all the default options to customize and
        # pass into the script's run method.
        self.options = InvectOptions().copy()


    def test_logging(self):
        """
        L{_InvectScript.run} adds a log observer which writes to the logfile
        specified by the L{_InvectScript} passed to it.
        """
        logging = []
        self.script._startLogging = self.spy(logging)

        logfile = self.options["logfile"] = self.mktemp()
        self.script.run(self.options)
        self.assertEqual([logfile], [fObj.name for fObj in logging])
        self.assertTrue(logging[0].closed)
        self.assertEqual(logging[0].mode, "a")


    def test_logfileParentCreated(self):
        """
        If the parent directory of the log file does not exist,
        L{_InvectScript.run} creates it.
        """
        parent = FilePath(self.mktemp())
        logfile = parent.child("invective.log")

        logging = []
        self.script._startLogging = self.spy(logging)
        self.options["logfile"] = logfile.path
        self.script.run(self.options)
        self.assertTrue(parent.exists())


    def test_parentCreationErrorsReported(self):
        """
        If the parent directory of the log file does not exist and there is an
        error creating it, the error propagates out of L{_InvectScript.run}.
        """
        parent = FilePath(self.mktemp())
        parent.touch()
        logfile = parent.child("invective.log")

        logging = []
        self.script._startLogging = self.spy(logging)
        self.options["logfile"] = logfile.path
        exc = self.assertRaises(EnvironmentError, self.script.run, self.options)
        self.assertEqual(ENOTDIR, exc.errno)



class ScriptTests(SynchronousTestCase, ScriptTestsMixin):
    """
    Tests for I{bin/invective}, the command-line entrypoint into invective.
    """
    def test_invective(self):
        """
        The I{bin/invective} script is runnable and does not exit early with any
        unhandled exceptions.
        """
        self.scriptTest("invective")
