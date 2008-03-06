
"""
Tests for the input widget.
"""

from twisted.trial.unittest import TestCase

from twisted.conch.insults.insults import ServerProtocol

from invective.widgets import LineInputWidget
from invective.history import History


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


    def test_initialization(self):
        """
        Verify that the input buffer, kill ring, and input history all start
        empty, and at the cursor begins at the beginning of the line.
        """
        self.assertEqual(self.widget.buffer, '')
        self.assertEqual(self.widget.cursor, 0)
        self.assertEqual(self.widget.killRing, [])
        self.assertEqual(self.widget.getInputHistory(), [])


    def test_setInputHistory(self):
        """
        Verify that the input history can be explicitly set via
        L{History.setInputHistory}.
        """
        self.widget.setInputHistory(History(["a", "b", "c"]))
        self.assertEqual(self.widget.getInputHistory(), ["a", "b", "c"])


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


    def test_delete(self):
        """
        Test that a delete keystroke removes a character from beneath the
        cursor.
        """
        s = 'hello world'
        n = 5
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.keystrokeReceived(ServerProtocol.DELETE, None)
        self.failUnless(self.painted)
        self.assertEqual(self.widget.buffer, s[:n] + s[n + 1:])
        self.assertEqual(self.widget.cursor, n)


    def test_deleteWhenEmpty(self):
        """
        Test that a delete keystroke when the buffer is empty does nothing.
        """
        self.widget.keystrokeReceived(ServerProtocol.DELETE, None)
        self.failIf(self.painted)
        self.assertEqual(self.widget.buffer, '')
        self.assertEqual(self.widget.cursor, 0)


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


    def test_unhandledFunction(self):
        """
        Verify that an unhandled function key has no consequences.
        """
        class Secret(object):
            """
            A special modifier which exists on no keyboard.
            """
            name = "SECRET"

        self.widget.keystrokeReceived('a', Secret())
        self.assertEqual(self.widget.buffer, '')
        self.assertEqual(self.widget.cursor, 0)


    def test_unhandledControl(self):
        """
        Verify that an unhandled C- combo doesn't alter the widget state.
        """
        s = 'hello world'
        n = 5
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.killRing = ['a', 'b']
        self.widget.keystrokeReceived('\x03', None)
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, n)
        self.assertEqual(self.widget.killRing, ['a', 'b'])


    def _homeTest(self, key):
        self.widget.keystrokeReceived('X', None)
        self.painted = False
        self.widget.keystrokeReceived(key, None)
        self.failUnless(self.painted)
        self.assertEqual(self.widget.cursor, 0)
        self.assertEqual(self.widget.buffer, 'X')


    def test_homeFunctionKey(self):
        """
        Test that the home key moves the cursor to the beginning of the line.
        """
        return self._homeTest(ServerProtocol.HOME)


    def test_home(self):
        """
        Test that C-a moves the cursor to the beginning of the line.
        """
        return self._homeTest('\x01')


    def _endTest(self, key):
        self.widget.keystrokeReceived('X', None)
        self.widget.cursor = 0
        self.painted = False
        self.widget.keystrokeReceived(key, None)
        self.failUnless(self.painted)
        self.assertEqual(self.widget.cursor, 1)
        self.assertEqual(self.widget.buffer, 'X')

    def test_endFunctionKEy(self):
        """
        Test that the end key moves the cursor to the end of the line.
        """
        return self._endTest(ServerProtocol.END)


    def test_end(self):
        """
        Test that C-e moves the cursor to the end of the line.
        """
        return self._endTest('\x05')


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


    def test_yank(self):
        """
        Verify that C-y inserts the active element in the kill ring at the
        current cursor position.
        """
        s = 'hello world'
        n = 5
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.killRing = ['one', 'two', 'three']
        self.widget.keystrokeReceived('\x19', None) # C-y
        self.assertEqual(self.widget.buffer, s[:n] + 'three' + s[n:])
        self.assertEqual(self.widget.cursor, n + len('three'))


    def test_yankWithoutKillRing(self):
        """
        Verify that C-y with an empty kill ring does nothing.
        """
        s = 'hello world'
        n = 5
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.killRing = []
        self.widget.keystrokeReceived('\x19', None)
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, n)


    def test_yankPop(self):
        """
        Verify that M-y cycles through the kill ring, replacing the previously
        yanked value with the next element from the kill ring.
        """
        s = 'hello world'
        n = 5
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.killRing = ['one', 'two', 'three']
        self.widget.keystrokeReceived('\x19', None) # C-y
        self.widget.keystrokeReceived('y', ServerProtocol.ALT)
        self.assertEqual(self.widget.buffer, s[:n] + 'two' + s[n:])
        self.assertEqual(self.widget.cursor, n + len('two'))
        self.assertEqual(self.widget.killRing, ['three', 'one', 'two'])


    def test_yankPopWithOneKilled(self):
        """
        Verify that M-y works properly if there is exactly one string in the
        kill ring.
        """
        s = 'hello world'
        n = 5
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.killRing = ['one']
        self.widget.keystrokeReceived('\x19', None)
        self.widget.keystrokeReceived('y', ServerProtocol.ALT)
        self.assertEqual(self.widget.buffer, s[:n] + 'one' + s[n:])
        self.assertEqual(self.widget.cursor, n + len('one'))
        self.assertEqual(self.widget.killRing, ['one'])


    def test_yankPopTwice(self):
        """
        Verify that M-y twice in a row after C-y properly cycles through the
        kill ring.
        """
        s = 'hello world'
        n = 5
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.killRing = ['last', 'second', 'first']
        self.widget.keystrokeReceived('\x19', None)
        self.widget.keystrokeReceived('y', ServerProtocol.ALT)
        self.widget.keystrokeReceived('y', ServerProtocol.ALT)
        self.assertEqual(self.widget.buffer, s[:n] + 'last' + s[n:])
        self.assertEqual(self.widget.cursor, n + len('last'))
        self.assertEqual(self.widget.killRing, ['second', 'first', 'last'])


    def test_yankPopWithoutYank(self):
        """
        Verify that M-y does nothing if not preceeded by C-y.
        """
        s = 'hello world'
        n = 5
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.killRing = ['one']
        self.widget.keystrokeReceived('y', ServerProtocol.ALT)
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, n)
        self.assertEqual(self.widget.killRing, ['one'])


    def test_yankPopAfterNotYank(self):
        """
        Verify that any command inserted between a C-y and an M-y disrupts the
        M-y.
        """
        s = 'hello world'
        n = 5
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.killRing = ['one']
        self.widget.keystrokeReceived('\x19', None)
        self.widget.keystrokeReceived('x', None)
        self.widget.keystrokeReceived('y', ServerProtocol.ALT)
        self.assertEqual(self.widget.buffer, s[:n] + 'onex' + s[n:])
        self.assertEqual(self.widget.cursor, n + len('onex'))


    def test_forwardCharacter(self):
        """
        Verify that C-f moves the cursor forward one position.
        """
        s = 'hello world'
        n = 5
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.keystrokeReceived('\x06', None) # C-f
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, n + 1)


    def test_forwardCharacterAtEndOfBuffer(self):
        """
        Verify that C-f when the cursor is at the end of the buffer does
        nothing.
        """
        s = 'hello world'
        n = len(s)
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.keystrokeReceived('\x06', None) # C-f
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, n)


    def test_backwardCharacter(self):
        """
        Verify that C-b moves the cursor backward on position.
        """
        s = 'hello world'
        n = 5
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.keystrokeReceived('\x02', None) # C-b
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, n - 1)


    def test_backwardCharacterAtBeginningOfBuffer(self):
        """
        Verify that C-b when the cursor is at the beginning of the buffer
        does nothing.
        """
        s = 'hello world'
        n = 0
        self.widget.buffer = s
        self.widget.cursor = n
        self.widget.keystrokeReceived('\x02', None) # C-b
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, n)


    def test_enterAppendsHistory(self):
        """
        Verify that a non-empty line is added to the input history when enter
        is hit.
        """
        s = 'hello world'
        self.widget.keystrokeReceived('\r', None)
        self.assertEqual(self.widget.getInputHistory(), [])
        self.widget.buffer = s
        self.widget.keystrokeReceived('\r', None)
        self.assertEqual(self.widget.getInputHistory(), [s])


    def test_previousLine(self):
        """
        Verify that C-p replaces the current input buffer with the previous
        line from the input history.
        """
        s = 'hello world'
        self.widget.buffer = s
        self.widget.setInputHistory(History(['first', 'second', 'last']))
        self.widget.keystrokeReceived('\x10', None)
        self.assertEqual(self.widget.buffer, 'last')
        self.assertEqual(self.widget.cursor, 0)


    def test_previousLineTwice(self):
        """
        Verify that C-p twice in a row results in the 2nd to last line from
        the input history being placed in the input buffer.
        """
        s = 'hello world'
        self.widget.buffer = s
        self.widget.setInputHistory(History(['first', 'second', 'last']))
        self.widget.keystrokeReceived('\x10', None)
        self.widget.keystrokeReceived('\x10', None)
        self.assertEqual(self.widget.buffer, 'second')
        self.assertEqual(self.widget.cursor, 0)


    def test_previousLineWithoutHistory(self):
        """
        Verify that C-p when there is no input history does nothing.
        """
        s = 'hello world'
        self.widget.buffer = s
        self.widget.setInputHistory(History([]))
        self.widget.keystrokeReceived('\x10', None)
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, 0)
        self.assertEqual(self.widget.getInputHistory(), [])


    def test_previousLineEmptyBuffer(self):
        """
        Verify that an empty line is not added to the input history when C-p is
        received.
        """
        s = 'hello world'
        self.widget.setInputHistory(History([s]))
        self.widget.keystrokeReceived('\x10', None)
        self.assertEqual(self.widget.getInputHistory(), [s])
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, 0)


    def test_previousLineEmptyBufferWithoutHistory(self):
        """
        Verify that an empty line is not added to the input history when C-p is
        received and that no error occurs even if there is no input history.
        """
        self.widget.keystrokeReceived('\x10', None)
        self.assertEqual(self.widget.getInputHistory(), [])
        self.assertEqual(self.widget.buffer, '')
        self.assertEqual(self.widget.cursor, 0)


    def test_nextLine(self):
        """
        Verify that C-n replaces the current input buffer with the next line
        from the input history.
        """
        s = 'hello world'
        self.widget.buffer = s
        history = History(['first', 'second', 'last'])
        history.previousLine()
        history.previousLine()
        self.widget.setInputHistory(history)
        self.widget.keystrokeReceived('\x0e', None)
        self.assertEqual(self.widget.buffer, 'last')
        self.assertEqual(self.widget.cursor, 0)


    def test_nextLineAtEnd(self):
        """
        Verify that C-n does nothing to the input buffer when at the end of the
        input history.
        """
        s = 'hello world'
        self.widget.buffer = s
        self.widget.setInputHistory(History(['first', 'second', 'last']))
        self.widget.keystrokeReceived('\x0e', None)
        self.assertEqual(self.widget.buffer, s)
        self.assertEqual(self.widget.cursor, 0)


    def test_nextLineTwice(self):
        """
        Verify that C-n twice in a row results in the 2nd to first line from
        the input history being placed in the input buffer.
        """
        s = 'hello world'
        self.widget.buffer = s
        history = History(['first', 'second', 'last'])
        history.previousLine()
        history.previousLine()
        history.previousLine()
        self.widget.setInputHistory(history)
        self.widget.keystrokeReceived('\x0e', None)
        self.widget.keystrokeReceived('\x0e', None)
        self.assertEqual(self.widget.buffer, 'last')
        self.assertEqual(self.widget.cursor, 0)


    def test_nextLineEmptyBuffer(self):
        """
        Verify that an empty line is not added to the input history when C-n is
        received.
        """
        s = 'hello world'
        self.widget.setInputHistory(History([s]))
        self.widget.keystrokeReceived('\x0e', None)
        self.assertEqual(self.widget.getInputHistory(), [s])
        self.assertEqual(self.widget.buffer, "")
        self.assertEqual(self.widget.cursor, 0)


    def test_historyPositionResetByReturn(self):
        """
        Verify that C{'\r'} resets the history position to the end.
        """
        s1 = "hello"
        s2 = "world"
        s3 = "goodbye"
        history = History([s1, s2, s3])
        self.widget.setInputHistory(history)
        self.widget.keystrokeReceived('\x10', None) # put s3 up
        self.widget.keystrokeReceived('\x10', None) # put s2 up
        self.widget.keystrokeReceived('\r', None) # submit s2

        # s2 should be the previous line now, since it was added to the input
        # history and the input history position was reset.
        self.assertEqual(history.previousLine(), s2)

        # Followed by s3, s2, and s1
        self.assertEqual(history.previousLine(), s3)
        self.assertEqual(history.previousLine(), s2)
        self.assertEqual(history.previousLine(), s1)


    def test_editBufferSaved(self):
        """
        Verify that the current edit buffer and cursor position is saved when
        traversing the history and restored when C{nextLine} is invoked at the
        end of the input history.
        """
        s1 = "hello"
        s2 = "world"
        n = 3
        history = History([s1])
        self.widget.buffer = s2
        self.widget.cursor = n
        self.widget.setInputHistory(history)
        self.widget.keystrokeReceived('\x10', None)
        self.assertEqual(self.widget.buffer, s1)
        self.widget.keystrokeReceived('\x0e', None)
        self.assertEqual(self.widget.buffer, s2)
        self.assertEqual(self.widget.cursor, n)
