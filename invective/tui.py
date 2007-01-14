# -*- test-case-name: invective.test -*-

"""
Create and arrange widgets to form an IRC client.
"""

from twisted.internet import reactor

from twisted.conch.insults.insults import TerminalProtocol, privateModes
from twisted.conch.insults.window import TopWindow, VBox, TextOutput

from invective.widgets import LineInputWidget, StatusWidget

# XXX TODO - Use Glade
def createChatRootWidget(width, height, painter, statusModel, controller):
    root = TopWindow(painter)
    vbox = VBox()
    vbox.addChild(TextOutput())
    vbox.addChild(StatusWidget(statusModel))
    vbox.addChild(LineInputWidget(width, controller))
    root.addChild(vbox)
    return root



class UserInterface(TerminalProtocol):
    """
    Set up an input area and an output area for a chat client.
    """
    width = 80
    height = 24

    def _painter(self):
        self.rootWidget.draw(self.width, self.height, self.terminal)


    def _controller(self, line):
        pass


    def connectionMade(self):
        super(UserInterface, self).connectionMade()
        self.terminal.eraseDisplay()
        self.terminal.resetPrivateModes([privateModes.CURSOR_MODE])
        self.rootWidget = createChatRootWidget(
            self.width - 2, self.height,
            self._painter, self, self._controller)


    def connectionLost(self, reason):
        reactor.stop()


    def keystrokeReceived(self, keyID, modifier):
        self.rootWidget.keystrokeReceived(keyID, modifier)


    # IStatusModel
    def focusedChannel(self):
        return None
