
"""
Tests for the top-level TUI code.
"""

from StringIO import StringIO

from twisted.trial.unittest import TestCase
from twisted.internet.error import TimeoutError
from twisted.conch.insults.window import TopWindow, VBox, TextOutput
from twisted.conch.insults.helper import TerminalBuffer
from twisted.conch.insults.insults import privateModes

from invective.widgets import LineInputWidget, StatusWidget
from invective.tui import createChatRootWidget, UserInterface


class WidgetLayoutTests(TestCase):
    """
    Test that widget objects end up in the right place in a widget hierarchy.
    """
    def test_rootCreation(self):
        """
        Verify that L{createChatRootWidget} gives back a L{TopWindow} with a
        L{TextOutput}, a L{StatusWidget}, and a L{LineInputWidget} as children.
        """
        def painter():
            pass

        def controller(line):
            pass

        statusModel = object()

        root = createChatRootWidget(80, 24, painter, statusModel, controller)
        self.failUnless(isinstance(root, TopWindow))
        self.assertIdentical(root.painter, painter)
        self.assertEqual(len(root.children), 1)
        vbox = root.children[0]
        self.failUnless(isinstance(vbox, VBox))
        self.assertEqual(len(vbox.children), 3)
        output, status, input = vbox.children
        self.failUnless(isinstance(output, TextOutput))
        self.failUnless(isinstance(status, StatusWidget))
        self.assertIdentical(status.model, statusModel)
        self.failUnless(isinstance(input, LineInputWidget))
        self.assertIdentical(input._realSubmit, controller)



class UserInterfaceTests(TestCase):
    """
    Test that the TerminalProtocol in charge of the user's terminal behaves in
    a bunch of desirable ways.
    """
    def setUp(self):
        self.transport = None
        self.terminal = TerminalBuffer()
        self.terminal.makeConnection(self.transport)
        self.protocol = UserInterface()


    def test_initialState(self):
        """
        Test that immediately after a connection is established the screen is
        cleared and cursor display is disabled.
        """
        # Scribble on the terminal so we can tell that it gets cleared.
        self.terminal.write('test bytes')
        self.protocol.makeConnection(self.terminal)
        self.failUnless(str(self.terminal).isspace())
        self.failIfIn(privateModes.CURSOR_MODE, self.terminal.privateModes)



class InputParsingTests(TestCase):
    """
    Tests for dealing with user input which may contain commands or be a
    message destined for the network.
    """
    def setUp(self):
        self.transport = None
        self.terminal = TerminalBuffer()
        self.terminal.makeConnection(self.transport)
        self.protocol = UserInterface()
        self.protocol.reactor = self
        self.protocol.makeConnection(self.terminal)

        self.tcpConnections = []
        self.delayedCalls = []


    def connectTCP(self, host, port, factory, timeout=30, bindAddress=''):
        self.tcpConnections.append((host, port, factory, timeout, bindAddress))


    def callLater(self, n, f, *a, **kw):
        self.delayedCalls.append((n, f, a, kw))


    def test_commandDispatch(self):
        """
        Verify that a line starting with C{/} and a word is dispatched to a
        function determined by that word.
        """
        dispatched = []
        self.protocol.cmd_DISPATCHTEST = dispatched.append
        self.protocol.parseInputLine('/dispatchtest')
        self.assertEqual(dispatched, ['/dispatchtest'])


    def test_serverCommand(self):
        """
        Verify that C{/server} is interpreted as a command to establish a new
        server connection.  Also some more things (that a connection attempt is
        made, that when it succeeds an IRC login is attempted over it with the
        right nickname).

        This is poorly factored.  IRC testing should be done elsewhere.
        Connection setup testing should be done elsewhere.
        """
        self.protocol.cmd_SERVER('/server irc.example.org')
        self.assertEqual(len(self.tcpConnections), 1)
        self.assertEqual(self.tcpConnections[0][:2], ('irc.example.org', 6667))
        factory = self.tcpConnections[0][2]
        protocol = factory.buildProtocol(('irc.example.org', 6667))
        transport = StringIO()
        protocol.makeConnection(transport)
        self.assertEqual(transport.getvalue(), '')
        self.assertEqual(len(self.delayedCalls), 1)

        self.protocol.nickname = 'testuser'

        n, f, a, kw = self.delayedCalls.pop()
        f(*a, **kw)

        self.assertEqual(
            transport.getvalue(),
            'NICK testuser\r\n'
            'USER testuser foo bar :None\r\n')

        output = str(self.terminal).splitlines()
        report = output.pop()
        for L in output:
            self.assertEqual(L, '')
        self.assertEqual(report, '== Connection to irc.example.org established.')


    def test_serverCommandFailedConnection(self):
        """
        Like L{test_serverCommand} but for a connection which fails.
        """
        self.protocol.cmd_SERVER('/server irc.example.org')
        self.assertEqual(len(self.tcpConnections), 1)
        self.assertEqual(self.tcpConnections[0][:2], ('irc.example.org', 6667))
        factory = self.tcpConnections[0][2]
        factory.clientConnectionFailed(None, TimeoutError("mock timeout"))

        output = str(self.terminal).splitlines()
        report = output.pop()
        for L in output:
            self.assertEqual(L, '')
        self.assertEqual(report, '== Connection to irc.example.org failed: TimeoutError')
