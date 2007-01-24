# -*- test-case-name: invective.test -*-

"""
Insults Widgets used by the Invective user-interface.
"""

from textwrap import wrap

from twisted.conch.insults.window import YieldFocus, Widget, TextInput, TextOutput

from invective import version


class LineInputWidget(TextInput):
    """
    Single-line input area with history and function keys.
    """

    def __init__(self, maxWidth, onSubmit):
        self._realSubmit = onSubmit
        self.killRing = []
        super(LineInputWidget, self).__init__(maxWidth, self._onSubmit)


    def _onSubmit(self, line):
        """
        Clear the current buffer and call the submit handler specified when
        this widget was created.
        """
        self.setText('')
        self._realSubmit(line)


    def func_HOME(self, modifier):
        """
        Handle the home function key by repositioning the cursor at the
        beginning of the input area.
        """
        self.cursor = 0


    def func_END(self, modifier):
        """
        Handle the end function key by repositioning the cursor just past the
        end of the text in the input area.
        """
        self.cursor = len(self.buffer)


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


    def keystrokeReceived(self, keyID, modifier):
        """
        Override the inherited behavior to track whether either the cursor
        position or buffer contents change and automatically request a repaint
        if either does.
        """
        buffer = self.buffer
        cursor = self.cursor
        super(LineInputWidget, self).keystrokeReceived(keyID, modifier)
        if self.buffer != buffer or self.cursor != cursor:
            self.repaint()


    def characterReceived(self, keyID, modifier):
        """
        Handle a single non-function key, possibly with a modifier.

        If there is no modifier, let the super class handle this.  Otherwise,
        dispatch to a function for the specific key and modifier present.
        """
        if modifier is not None:
            getattr(self, 'func_' + modifier.name + '_' + keyID)()
        elif ord(keyID) <= 26 and keyID != '\r':
            getattr(self, 'func_CTRL_' + chr(ord(keyID) + ord('a') - 1))()
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
