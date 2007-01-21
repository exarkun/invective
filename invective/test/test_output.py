
"""
Tests for the main text display widget.
"""

from StringIO import StringIO

from twisted.trial.unittest import TestCase
from twisted.conch.insults.helper import TerminalBuffer

from invective.widgets import OutputWidget


class TextOutputTests(TestCase):
    """
    Verify that L{OutputWidget} renders properly in different situations.
    """
    width = 80
    height = 24

    def setUp(self):
        self.transport = StringIO()
        self.terminal = TerminalBuffer()
        self.terminal.makeConnection(self.transport)
        self.widget = OutputWidget()

    def test_noMessages(self):
        """
        Verify that when an L{OutputWidget} has no messages it renders as blank.
        """
        self.widget.render(self.width, self.height, self.terminal)
        self.failUnless(str(self.terminal).isspace())


    def test_oneMessage(self):
        """
        Verify that a single message is rendered at the bottom of the terminal.
        """
        message = 'Hello, world'
        self.widget.addMessage(message)
        self.widget.render(self.width, self.height, self.terminal)
        output = str(self.terminal).splitlines()
        message = output.pop()
        for L in output:
            self.assertEqual(L, ' ' * self.width)
        self.assertEqual(message, message + ' ' * (self.width - len(message)))


    def test_twoMessages(self):
        """
        Verify that a second message is placed below a first message, moving
        the first message up.
        """
        firstMessage = 'Hello, world'
        self.widget.addMessage(firstMessage)
        self.widget.render(self.width, self.height, self.terminal)
        secondMessage = 'Second'
        self.widget.addMessage(secondMessage)
        self.widget.render(self.width, self.height, self.terminal)
        output = str(self.terminal).splitlines()
        second = output.pop()
        first = output.pop()
        for L in output:
            self.assertEqual(L, ' ' * self.width)
        self.assertEqual(first, firstMessage + ' ' * (self.width - len(firstMessage)))
        self.assertEqual(second, secondMessage + ' ' * (self.width - len(secondMessage)))


    def test_messageWrapping(self):
        """
        Verify that a message longer than the terminal is wide is wrapped
        appropriately.
        """
        # 18 characters
        message = 'very long message '

        # 90 characters
        longMessage = message * 5

        self.widget.addMessage(longMessage)
        self.widget.render(self.width, self.height, self.terminal)

        output = str(self.terminal).splitlines()
        secondLine = output.pop()
        firstLine = output.pop()
        for L in output:
            self.assertEqual(L, ' ' * self.width)
        self.assertEqual(firstLine, 'very long message ' * 4 + 'very    ')
        self.assertEqual(secondLine, '  long message' + ' ' * (self.width - 14))
