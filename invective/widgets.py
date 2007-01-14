# -*- test-case-name: invective.test.test_input -*-

"""
Insults Widgets used by the Invective user-interface.
"""


from twisted.conch.insults.window import TextInput

class LineInputWidget(TextInput):
    """
    Single-line input area with history and function keys.
    """

    def __init__(self, maxWidth, onSubmit):
        self._realSubmit = onSubmit
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


    def characterReceived(self, keyID, modifier):
        """
        Handle a single non-function key, possibly with a modifier.

        If there is no modifier, let the super class handle this.  Otherwise,
        dispatch to a function for the specific key and modifier present.
        """
        if modifier is not None:
            getattr(self, 'func_' + modifier.name + '_' + keyID)()
        else:
            super(LineInputWidget, self).characterReceived(keyID, modifier)
