
"""
Tests for the input widget.
"""

from twisted.trial.unittest import TestCase

from twisted.conch.insults.insults import ServerProtocol

from invective.widgets import LineInputWidget

class InputTests(TestCase):
    """
    Test line editing features provided by L{invective.widgets.LineInputWidget}.
    """
    maxWidth = 78


    def setUp(self):
        self.lines = []
        self.widget = LineInputWidget(self.maxWidth, self.lines.append)
        self.widget.parent = self
        self.painted = False
        self.dirty = False


    def repaint(self):
        self.painted = True


    def test_printable(self):
        """
        Test that the receipt of a printable character results in it being
        added to the input buffer at the cursor position.
        """
        s = 'hello word'
        for ch in s:
            self.widget.keystrokeReceived(ch, None)
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, len(s))
        self.widget.cursor -= 1
        self.widget.keystrokeReceived('l', None)
        self.assertEqual(self.widget.buffer, s[:-1] + 'l' + s[-1:])
        self.failUnless(self.painted)


    def test_backspace(self):
        """
        Test that a backspace keystroke removes a character from the buffer and
        moves the cursor back one position.
        """
        self.widget.keystrokeReceived('X', None)
        self.painted = False
        self.widget.keystrokeReceived(ServerProtocol.BACKSPACE, None)
        self.assertEqual(self.widget.cursor, 0)
        self.assertEqual(self.widget.buffer, '')
        self.failUnless(self.painted)


    def test_backspaceWhenEmpty(self):
        """
        Test that a backspace keystroke is a no-op when there are no bytes in
        the buffer.
        """
        self.widget.keystrokeReceived(ServerProtocol.BACKSPACE, None)
        self.failIf(self.painted)
        self.assertEqual(self.widget.cursor, 0)
        self.assertEqual(self.widget.buffer, '')


    def test_enter(self):
        """
        Test that the enter key submits a line, clears the buffer, and resets
        the cursor position.
        """
        s = 'words'
        for ch in s:
            self.widget.keystrokeReceived(ch, None)
        self.painted = False
        self.widget.keystrokeReceived('\r', None)
        self.failUnless(self.painted)
        self.assertEqual(self.lines, [s])
        self.assertEqual(self.widget.cursor, 0)
        self.assertEqual(self.widget.buffer, '')


    def test_home(self):
        """
        Test that the home key moves the cursor to the beginning of the line.
        """
        self.widget.keystrokeReceived('X', None)
        self.painted = False
        self.widget.keystrokeReceived(ServerProtocol.HOME, None)
        self.failUnless(self.painted)
        self.assertEqual(self.widget.cursor, 0)
        self.assertEqual(self.widget.buffer, 'X')


    def test_end(self):
        """
        Test that the end key moves the cursor to the end of the line.
        """
        self.widget.keystrokeReceived('X', None)
        self.widget.cursor = 0
        self.painted = False
        self.widget.keystrokeReceived(ServerProtocol.END, None)
        self.failUnless(self.painted)
        self.assertEqual(self.widget.cursor, 1)
        self.assertEqual(self.widget.buffer, 'X')


    def test_backwardWord(self):
        """
        Test that M-b moves the cursor to the beginning of the word currently
        under the cursor.
        """
        s = 'hello world'
        for ch in s:
            self.widget.keystrokeReceived(ch, None)
        self.painted = False
        self.widget.keystrokeReceived('b', ServerProtocol.ALT)
        self.failUnless(self.painted)
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, s.index('world'))
        self.painted = False
        self.widget.keystrokeReceived('b', ServerProtocol.ALT)
        self.failUnless(self.painted)
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, 0)


    def test_backwardWordWhenEmpty(self):
        """
        Test that M-b does nothing with an empty buffer.
        """
        self.widget.keystrokeReceived('b', ServerProtocol.ALT)
        self.failIf(self.painted)
        self.assertEqual(self.widget.cursor, 0)
        self.assertEqual(self.widget.buffer, '')


    def test_backwardWordFromBeginning(self):
        """
        Test that M-b at the beginning of a line does nothing.
        """
        self.widget.keystrokeReceived('X', None)
        self.widget.cursor = 0
        self.painted = False
        self.widget.keystrokeReceived('b', ServerProtocol.ALT)
        self.failIf(self.painted)
        self.assertEqual(self.widget.buffer, 'X')
        self.assertEqual(self.widget.cursor, 0)


    def test_forwardWord(self):
        """
        Test that M-f moves to just after the end of the word currently under
        the cursor.
        """
        s = 'hello world'
        for ch in s:
            self.widget.keystrokeReceived(ch, None)
        self.widget.cursor = 0
        self.painted = False
        self.widget.keystrokeReceived('f', ServerProtocol.ALT)
        self.failUnless(self.painted)
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, s.index(' '))
        self.painted = False
        self.widget.keystrokeReceived('f', ServerProtocol.ALT)
        self.failUnless(self.painted)
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, len(s))


    def test_forwardWordWhenEmpty(self):
        """
        Test that M-f does nothing with an empty buffer.
        """
        self.widget.keystrokeReceived('f', ServerProtocol.ALT)
        self.failIf(self.painted)
        self.assertEqual(self.widget.buffer, '')
        self.assertEqual(self.widget.cursor, 0)


    def test_forwardWordAtEnd(self):
        """
        Test that M-f at the end of a line does nothing.
        """
        self.widget.keystrokeReceived('X', None)
        self.painted = False
        self.widget.keystrokeReceived('f', ServerProtocol.ALT)
        self.failIf(self.painted)
        self.assertEqual(self.widget.buffer, 'X')
        self.assertEqual(self.widget.cursor, 1)


    def test_emptyKill(self):
        """
        Verify that if C-k is received when the cursor is at the end of the
        buffer, no state changes.
        """
        s = 'hello world'
        self.widget.buffer = s
        self.widget.cursor = len(s)
        self.widget.keystrokeReceived('\x0b', None) # C-k
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.killRing, [])


    def test_kill(self):
        """
        Verify that C-k deletes from the cursor to the end of the line and adds
        that text to the kill ring.
        """
        s = 'hello world'
        n = 5
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.keystrokeReceived('\x0b', None) # C-k
        self.assertEqual(self.widget.buffer, s[:n])
        self.assertEqual(self.widget.killRing, [s[n:]])
