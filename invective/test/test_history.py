
"""
Tests for input history tracking as provided by L{History}.
"""

from twisted.trial.unittest import TestCase

from invective.history import History


class HistoryTests(TestCase):
    """
    Tests for L{History}'s tracking of input lines.
    """
    def test_allLinesWhenEmpty(self):
        """
        Verify that retrieving all lines at once from an empty history object
        returns an empty list.
        """
        h = History()
        self.assertEqual(h.allLines(), [])


    def test_createWithLines(self):
        """
        Verify that a history object can be created with an initial set of
        lines.
        """
        h = History(["a", "b"])
        self.assertEqual(h.allLines(), ["a", "b"])


    def test_addLineWhenEmpty(self):
        """
        Verify that a line added to an empty history object results in that
        line being included in the list returned by C{allLines}.
        """
        s = "hello world"
        h = History([s])
        self.assertEqual(h.allLines(), [s])


    def test_addLineAtEnd(self):
        """
        Verify that, by default, a line added to a history object is added
        after any existing lines.
        """
        s1 = "hello"
        s2 = "world"
        h = History([s1])
        h.addLine(s2)
        self.assertEqual(h.allLines(), [s1, s2])


    def test_addLineInMiddle(self):
        """
        Verify that even if the history object is not positioned at the end,
        C{addLine} adds the line to the end.
        """
        s1 = "hello"
        s2 = "world"
        s3 = "goodbye"
        h = History([s1, s2])
        h.previousLine()
        h.addLine(s3)
        self.assertEqual(h.allLines(), [s1, s2, s3])


    def test_previousLineWithNoLines(self):
        """
        Verify that retrieving the previous line from an empty history object
        returns an empty string.
        """
        h = History()
        self.assertEqual(h.previousLine(), "")


    def test_previousLineWithOneLine(self):
        """
        Verify that when there is a line in the history object, C{previousLine}
        returns it.
        """
        s = "hello"
        h = History([s])
        self.assertEqual(h.previousLine(), s)
        self.assertEqual(h.previousLine(), "")


    def test_previousLineWithTwoLines(self):
        """
        Verify that when the history object is positioned somewhere in the
        middle, C{previousLine} returns the previous line.
        """
        s1 = "hello"
        s2 = "world"
        h = History([s1, s2])
        self.assertEqual(h.previousLine(), s2)
        self.assertEqual(h.previousLine(), s1)
        self.assertEqual(h.previousLine(), "")


    def test_nextLineWithNoLines(self):
        """
        Verify that retrieving the next line from an empty history object
        returns an empty string.
        """
        h = History()
        self.assertEqual(h.nextLine(), "")


    def test_nextLineWithOneLine(self):
        """
        Verify that when positioned at the beginning and containing only one
        line, the history object's C{nextLine} method returns an empty string.
        """
        s = "hello"
        h = History([s])
        while h.previousLine():
            pass
        self.assertEqual(h.nextLine(), "")


    def test_nextLineWithTwoLines(self):
        """
        Verify that when a history object contains two lines and is positioned
        at the beginning, C{nextLine} first returns the second line and then
        returns an empty string.
        """
        s1 = "hello"
        s2 = "world"
        h = History([s1, s2])
        while h.previousLine():
            pass
        self.assertEqual(h.nextLine(), s2)
        self.assertEqual(h.nextLine(), "")


    def test_resetPosition(self):
        """
        Verify that the position in the history object can be set to the end
        using the C{resetPosition} method.
        """
        s = "hello"
        h = History()
        h.addLine(s)
        h.previousLine()
        h.resetPosition()
        self.assertEqual(h.nextLine(), "")
