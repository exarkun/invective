
"""
Tests for the top-level TUI code.
"""

from twisted.trial.unittest import TestCase
from twisted.conch.insults.window import TopWindow, VBox, TextOutput
from twisted.conch.insults.helper import TerminalBuffer
from twisted.conch.insults.insults import privateModes

from invective.widgets import LineInputWidget
from invective.tui import createChatRootWidget, UserInterface


class WidgetLayoutTests(TestCase):
    """
    Test that widget objects end up in the right place in a widget hierarchy.
    """
    def test_rootCreation(self):
        """
        Verify that L{createChatRootWidget} gives back a L{TopWindow} with a
        L{TextOutput} and a L{LineInputWidget} as children.
        """
        def painter():
            pass

        def controller(line):
            pass

        root = createChatRootWidget(80, 24, painter, controller)
        self.failUnless(isinstance(root, TopWindow))
        self.assertIdentical(root.painter, painter)
        self.assertEqual(len(root.children), 1)
        vbox = root.children[0]
        self.failUnless(isinstance(vbox, VBox))
        self.assertEqual(len(vbox.children), 2)
        output, input = vbox.children
        self.failUnless(isinstance(output, TextOutput))
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
        # And explicitly enable the cursor, although I think it is probably the
        # case that this should be the default mode.
        self.terminal.setModes([privateModes.CURSOR_MODE])

        self.protocol.makeConnection(self.terminal)
        self.failUnless(str(self.terminal).isspace())
        self.failIfIn(privateModes.CURSOR_MODE, self.terminal.modes)
