# -*- test-case-name: invective.test -*-

"""
Create and arrange widgets to form an IRC client.
"""

from signal import signal, SIGWINCH
from fcntl import ioctl
from tty import TIOCGWINSZ
from struct import unpack

from twisted.internet import reactor

from twisted.words.im.ircsupport import IRCAccount

from twisted.conch.insults.insults import TerminalProtocol, privateModes
from twisted.conch.insults.window import TopWindow, VBox

from invective.widgets import LineInputWidget, StatusWidget, OutputWidget
from invective.chat import InvectiveChatUI

# XXX TODO - Use Glade
def createChatRootWidget(reactor, width, height, painter, statusModel, controller):
    def _schedule(f):
        reactor.callLater(0, f)
    root = TopWindow(painter, _schedule)
    root.reactor = reactor
    vbox = VBox()
    vbox.addChild(OutputWidget())
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

    group = None
    client = None

    reactor = reactor

    def connectionMade(self):
        super(UserInterface, self).connectionMade()
        self.terminal.eraseDisplay()
        self.terminal.resetPrivateModes([privateModes.CURSOR_MODE])
        self.rootWidget = createChatRootWidget(
            self.reactor,
            self.width - 2, self.height,
            self._painter, self, self.parseInputLine)

        # XXX rootWidget obviously needs a richer interface
        self.ui = InvectiveChatUI(self.rootWidget.children[0].children[0])


    def _painter(self):
        self.rootWidget.draw(self.width, self.height, self.terminal)


    def statusChanged(self):
        self.rootWidget.children[0].children[1].repaint()


    def addOutputMessage(self, msg):
        return self.rootWidget.children[0].children[0].addMessage(msg)


    def newServerConnection(self, host, username):
        account = IRCAccount(
            "IRC",
            True,
            username,
            None,
            host,
            6667,
            "")
        def cbLogOn(client):
            self.client = client
            self.addOutputMessage("== Connection to %s established." % (host,))
        def ebLogOn(err):
            self.addOutputMessage("== %s failed: %s" % (host, err.getErrorMessage()))
        account.logOn(self.ui).addCallbacks(cbLogOn, ebLogOn)


    def cmd_JOIN(self, line):
        if self.client is None:
            self.addOutputMessage('== no server')
        else:
            channel = line.split()[1][1:]
            self.client.joinGroup(channel)
            self.group = self.client.getGroupConversation(channel)
            self.statusChanged()


    def cmd_PART(self, line):
        if self.client is None:
            self.addOutputMessage('== no server')
        else:
            channel = line.split()[1][1:]
            self.client.leaveGroup(channel)
            self.group = None
            self.statusChanged()


    def cmd_QUIT(self, line):
        self.terminal.setPrivateModes([privateModes.CURSOR_MODE])
        self.terminal.loseConnection()


    def cmd_SERVER(self, line):
        """
        Establish a new connection to a server.

        @type line: C{str}
        @param line: A string of the form '/server <server hostname> <username>'.
        """
        if self.client is not None:
            self.addOutputMessage('== already connected')
        else:
            hostname, username = line.split()[1:]
            self.newServerConnection(hostname, username)


    def parseInputLine(self, line):
        if line[:1] == '/':
            special = getattr(self, 'cmd_' + line[1:].split()[0].upper(), None)
            if special is not None:
                special(line)
            else:
                self.addOutputMessage('== no such command')
        else:
            if self.group is None:
                self.addOutputMessage('== no channel')
            else:
                self.group.sendText(line)
                self.group.showGroupMessage(self.group.group.account.username, line, {})


    def keystrokeReceived(self, keyID, modifier):
        self.rootWidget.keystrokeReceived(keyID, modifier)


    def terminalSize(self, width, height):
        self.width = width
        self.height = height
        self._painter()


    # IStatusModel
    def focusedChannel(self):
        if self.group is not None:
            return self.group.group.name
        return None


    # IChatObserver
    def messageReceived(self, user, channel, message):
        self.addOutputMessage('[%s] <%s> %s' % (channel, user, message))


    def channelJoined(self, channel):
        self.addOutputMessage('== joined %s' % (channel,))


    def channelLeft(self, channel):
        self.addOutputMessage('== left %s' % (channel,))
        if channel == self.channel:
            self.channel = None
            self.statusChanged()


    def userJoined(self, channel, nick):
        self.addOutputMessage('== %s joined %s' % (nick, channel))


    def userLeft(self, channel, nick):
        self.addOutputMessage('== %s left %s' % (nick, channel))



class CommandLineUserInterface(UserInterface):
    def connectionMade(self):
        signal(SIGWINCH, self.windowChanged)
        winSize = self.getWindowSize()
        self.width = winSize[0]
        self.height = winSize[1]
        super(CommandLineUserInterface, self).connectionMade()


    def connectionLost(self, reason):
        reactor.stop()


    # XXX Should be part of runWithProtocol
    def getWindowSize(self):
        winsz = ioctl(0, TIOCGWINSZ, '12345678')
        winSize = unpack('4H', winsz)
        newSize = winSize[1], winSize[0], winSize[3], winSize[2]
        return newSize


    def windowChanged(self, signum, frame):
        winSize = self.getWindowSize()
        self.terminalSize(winSize[0], winSize[1])
