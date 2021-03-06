# -*- test-case-name: invective.test -*-

"""
Insults Widgets used by the Invective user-interface.
"""

from textwrap import wrap

from twisted.conch.insults.insults import ServerProtocol
from twisted.conch.insults.window import YieldFocus, Widget, TextInput, TextOutput

from invective import version
from invective.history import History


class LineInputWidget(TextInput):
    """
    Single-line input area with history and function keys.

    @ivar previousKeystroke: A reference to the most recently received
    keystroke, updated after each keystroke is processed.

    @ivar killRing: A list of killed strings, in order of oldest to newest.

    @type savedBuffer: C{NoneType} or C{str}
    @ivar savedBuffer: The string in the edit buffer at the time a history
    traversal command was first invoked, or C{None} if the history is not
    currently being traversed.
    """

    previousKeystroke = None
    savedBuffer = None

    def __init__(self, maxWidth, onSubmit):
        self._realSubmit = onSubmit
        self.killRing = []
        self.setInputHistory(History())
        super(LineInputWidget, self).__init__(maxWidth, self._onSubmit)


    def setInputHistory(self, history):
        """
        Set the complete input history to the given history object.
        """
        self.inputHistory = history


    def getInputHistory(self):
        """
        Retrieve a list of lines representing the current input history.
        """
        return self.inputHistory.allLines()


    def _onSubmit(self, line):
        """
        Clear the current buffer and call the submit handler specified when
        this widget was created.
        """
        if line:
            self.inputHistory.addLine(line)
            self.inputHistory.resetPosition()
            self.setText('')
        self._realSubmit(line)


    def func_HOME(self, modifier):
        """
        Handle the home function key by repositioning the cursor at the
        beginning of the input area.
        """
        self.cursor = 0


    def func_CTRL_a(self):
        """
        Handle C-a in the same way as the home function key.
        """
        return self.func_HOME(None)


    def func_CTRL_f(self):
        """
        Handle C-f to move the cursor forward one position.
        """
        self.cursor = min(self.cursor + 1, len(self.buffer))


    def func_CTRL_b(self):
        """
        Handle C-b to move the cursor forward one position.
        """
        self.cursor = max(self.cursor - 1, 0)


    def func_END(self, modifier):
        """
        Handle the end function key by repositioning the cursor just past the
        end of the text in the input area.
        """
        self.cursor = len(self.buffer)


    def func_CTRL_e(self):
        """
        Handle C-e in the same way as the end function key.
        """
        return self.func_END(None)


    def func_ALT_b(self):
        """
        Handle M-b by moving the cursor to the beginning of the word under the
        current cursor position.  Do nothing at the beginning of the line.
        Words are considered non-whitespace characters delimited by whitespace
        characters.
        """
        while self.cursor > 0 and self.buffer[self.cursor - 1].isspace():
            self.cursor -= 1
        while self.cursor > 0 and not self.buffer[self.cursor - 1].isspace():
            self.cursor -= 1


    def func_ALT_f(self):
        """
        Handle M-f by moving the cursor to just after the end of the word under
        the current cursor position.  Do nothing at the end of the line.  Words
        are considered non-whitespace characters delimited by whitespace
        characters.
        """
        n = len(self.buffer)
        while self.cursor < n and self.buffer[self.cursor].isspace():
            self.cursor += 1
        while self.cursor < n and not self.buffer[self.cursor].isspace():
            self.cursor += 1


    def func_CTRL_k(self):
        """
        Handle C-k by truncating the line from the character beneath the cursor
        and adding the removed text to the kill ring.
        """
        chopped = self.buffer[self.cursor:]
        self.buffer = self.buffer[:self.cursor]
        if chopped:
            self.killRing.append(chopped)


    def func_CTRL_y(self):
        """
        Handle C-y by inserting an element from the kill ring at the current
        cursor position, moving the cursor to the end of the inserted text.
        """
        if self.killRing:
            insert = self.killRing[-1]
            self.buffer = self.buffer[:self.cursor] + insert + self.buffer[self.cursor:]
            self.cursor += len(insert)


    def func_ALT_y(self):
        """
        Handle M-y by cycling the kill ring and replacing the previously yanked
        text with the new final element in the ring.
        """
        if self.previousKeystroke in (('\x19', None), ('y', ServerProtocol.ALT)): # C-y and M-y
            previous = self.killRing.pop()
            self.killRing.insert(0, previous)
            next = self.killRing[-1]

            self.cursor -= len(previous)
            self.buffer = self.buffer[:self.cursor] + next + self.buffer[self.cursor + len(previous):]
            self.cursor += len(next)


    def func_CTRL_p(self):
        """
        Handle C-p to swap the current input buffer with the previous line from
        input history.
        """
        if not self.inputHistory.afterLines:
            # Going from normal editing to history traversal - save the edit
            # buffer.
            self.savedBuffer = self.buffer
        previousLine = self.inputHistory.previousLine()
        if previousLine:
            self.buffer = previousLine


    def func_CTRL_n(self):
        """
        Handle C-n to swap the current input buffer with the next line from
        input history.
        """
        nextLine = self.inputHistory.nextLine()
        if nextLine:
            self.buffer = nextLine
        else:
            if self.savedBuffer is not None:
                self.buffer = self.savedBuffer
                self.savedBuffer = None


    def func_DELETE(self, modifier):
        """
        Handle delete to remove the character beneath the cursor.
        """
        self.buffer = self.buffer[:self.cursor] + self.buffer[self.cursor + 1:]


    def keystrokeReceived(self, keyID, modifier):
        """
        Override the inherited behavior to track whether either the cursor
        position or buffer contents change and automatically request a repaint
        if either does.
        """
        buffer = self.buffer
        cursor = self.cursor
        super(LineInputWidget, self).keystrokeReceived(keyID, modifier)
        self.previousKeystroke = (keyID, modifier)
        if self.buffer != buffer or self.cursor != cursor:
            self.repaint()


    def characterReceived(self, keyID, modifier):
        """
        Handle a single non-function key, possibly with a modifier.

        If there is no modifier, let the super class handle this.  Otherwise,
        dispatch to a function for the specific key and modifier present.
        """
        if modifier is not None:
            f = getattr(self, 'func_' + modifier.name + '_' + keyID, None)
            if f is not None:
                f()
        elif ord(keyID) <= 26 and keyID != '\r':
            f = getattr(self, 'func_CTRL_' + chr(ord(keyID) + ord('a') - 1), None)
            if f is not None:
                f()
        else:
            super(LineInputWidget, self).characterReceived(keyID, modifier)



class StatusWidget(Widget):
    """
    Display status information such as channel activity and modes.
    """
    def __init__(self, statusModel):
        super(StatusWidget, self).__init__()
        self.model = statusModel


    def sizeHint(self):
        """
        Hint to the containing widget how large this widget should be.

        There is always only one line of status information, so request a
        height of one.  We will try to cope with any width, so do not provide a
        width hint.
        """
        return (None, 1)


    def focusReceived(self):
        """
        Reject focus whenever it comes to us.
        """
        raise YieldFocus()


    def render(self, width, height, terminal):
        """
        Display invective version information and information about the state
        of the model we were constructed with.
        """
        info = {'version': version}
        chan = self.model.focusedChannel()
        if chan is None:
            chan = '(No Channel)'
        info['focusedChannel'] = chan

        terminal.cursorPosition(0, 0)
        status = '[%(version)s] %(focusedChannel)s' % info
        terminal.write(status + ' ' * (width - len(status)))



class OutputWidget(TextOutput):
    def __init__(self, size=None):
        super(OutputWidget, self).__init__(size)
        self.messages = []


    def formatMessage(self, s, width):
        return wrap(s, width=width, subsequent_indent="  ")


    def addMessage(self, message):
        self.messages.append(message)
        self.repaint()


    def render(self, width, height, terminal):
        output = []
        for i in xrange(len(self.messages) - 1, -1, -1):
            output[:0] = self.formatMessage(self.messages[i], width - 2)
            if len(output) >= height:
                break
        if len(output) < height:
            output[:0] = [''] * (height - len(output))
        for n, L in enumerate(output):
            terminal.cursorPosition(0, n)
            terminal.write(L + ' ' * (width - len(L)))
