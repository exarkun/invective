
"""
Test the status display widget.
"""

from twisted.trial.unittest import TestCase
from twisted.conch.insults.helper import TerminalBuffer
from twisted.conch.insults.window import YieldFocus

from invective.widgets import StatusWidget
from invective import version

class DummyModel(object):
    def __init__(self, focusedChannel):
        self._focChan = focusedChannel


    def focusedChannel(self):
        return self._focChan



class StatusWidgetTests(TestCase):
    """
    Tests for the state tracking behavior of the status model object.
    """
    width = 80
    height = 1

    def setUp(self):
        """
        Create a dummy terminal transport to test widgets against.
        """
        self.transport = None
        self.terminal = TerminalBuffer()
        self.terminal.width = self.width
        self.terminal.height = self.height
        self.terminal.makeConnection(self.transport)


    def test_sizeHint(self):
        """
        Verify that the status widget asks for only one line of display area.
        """
        status = StatusWidget(DummyModel(None))
        self.assertEqual(status.sizeHint(), (None, 1))


    def test_rejectFocus(self):
        """
        Verify that the status widget will not take focus.
        """
        status = StatusWidget(DummyModel(None))
        self.assertRaises(YieldFocus, status.focusReceived)


    def test_noChannelRendering(self):
        """
        Verify that the status widget renders properly when there is no focused
        channel in its model.
        """
        status = StatusWidget(DummyModel(None))
        status.render(self.width, self.height, self.terminal)
        expected = '[%s] (No Channel)' % (version,)
        self.assertEqual(str(self.terminal), expected + ' ' * (self.width - len(expected)))


    def test_withChannelRendering(self):
        """
        Verify that the status widget renders properly when there is a focused
        channel in its model.
        """
        channel = '#example'
        status = StatusWidget(DummyModel(channel))
        status.render(self.width, self.height, self.terminal)
        expected = '[%s] %s' % (version, channel)
        self.assertEqual(str(self.terminal), expected + ' ' * (self.width - len(expected)))


    def test_shortenedStatus(self):
        """
        Verify that if a new status is shorter than the previous status, the
        previous status is completely erased.
        """
        longChannel = '#long-channel-name'
        shortChannel = '#short'
        status = StatusWidget(DummyModel(longChannel))
        status.render(self.width, self.height, self.terminal)
        status = StatusWidget(DummyModel(shortChannel))
        status.render(self.width, self.height, self.terminal)
        expected = '[%s] %s' % (version, shortChannel)
        self.assertEqual(str(self.terminal), expected + ' ' * (self.width - len(expected)))
