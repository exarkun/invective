# -*- test-case-name: invective.test.test_history -*-

"""
Self-contained input history representation.
"""

class History(object):
    """
    @type beforeLines: C{list} of C{str}
    @ivar beforeLines: The lines in this history which come before the current position.

    @type afterLines: C{list} of C{str}
    @ivar afterLines: The lines in this history which come after the current position.
    """

    def __init__(self, lines=None):
        if lines is None:
            lines = []
        self.beforeLines = lines
        self.afterLines = []


    def nextLine(self):
        """
        Advance the position by one and return the line there, or an empty
        string if there is no next line.
        """
        if self.afterLines:
            self.beforeLines.append(self.afterLines.pop(0))
            if self.afterLines:
                return self.afterLines[0]
            return ""
        return ""


    def previousLine(self):
        """
        Rewind the position by one and return the line there, or an empty
        string if there is no previous line.
        """
        if self.beforeLines:
            self.afterLines.insert(0, self.beforeLines.pop())
            return self.afterLines[0]
        return ""


    def allLines(self):
        """
        Return a list of all lines in this history object.
        """
        return self.beforeLines + self.afterLines


    def addLine(self, line):
        """
        Add a new line to the end of this history object.
        """
        if self.afterLines:
            self.afterLines.append(line)
        else:
            self.beforeLines.append(line)


    def resetPosition(self):
        """
        Set the position in the input history to the end.
        """
        self.beforeLines.extend(self.afterLines)
        self.afterLines = []
