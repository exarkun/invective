# -*- test-case-name: invective.test -*-

"""
Create and arrange widgets to form an IRC client.
"""

from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator

from twisted.conch.insults.insults import TerminalProtocol, privateModes
from twisted.conch.insults.window import TopWindow, VBox

from invective.widgets import LineInputWidget, StatusWidget, OutputWidget
from invective.irc import IRCClient

# XXX TODO - Use Glade
def createChatRootWidget(reactor, width, height, painter, statusModel, controller):
    root = TopWindow(painter)
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

    channel = None
    proto = None

    reactor = reactor

    def _painter(self):
        self.rootWidget.draw(self.width, self.height, self.terminal)


    def addOutputMessage(self, msg):
        return self.rootWidget.children[0].children[0].addMessage(msg)


    def newServerConnection(self, kind, host):
        protocol = IRCClient(self)
        return ClientCreator(self.reactor, lambda: protocol).connectTCP(host, 6667)


    def cmd_JOIN(self, line):
        if self.proto is None:
            self.addOutputMessage('== no server')
        else:
            channel = line.split()[1]
            self.proto.join(channel)
            self.channel = channel


    def cmd_PART(self, line):
        if self.proto is None:
            self.addOutputMessage('== no server')
        else:
            channel = line.split()[1]
            self.proto.part(channel)
            self.channel = None


    def cmd_QUIT(self, line):
        self.terminal.setPrivateModes([privateModes.CURSOR_MODE])
        self.terminal.loseConnection()


    def _cbNewServerConnection(self, proto, host, nickname):
        self.addOutputMessage('== Connection to %s established.' % (host,))
        proto.register(nickname)
        self.proto = proto
        self.nickname = nickname


    def _ebNewServerConnection(self, err, host):
        self.addOutputMessage('== %s failed: %s' % (host, err.getErrorMessage()))


    def cmd_SERVER(self, line):
        """
        Establish a new connection to a server.

        @type line: C{str}
        @param line: A string of the form '/server <server hostname> <username>'.
        """
        if self.proto is not None:
            self.addOutputMessage('== already connected')
        else:
            hostname, username = line.split()[1:]
            d = self.newServerConnection('irc', hostname)
            d.addCallbacks(
                self._cbNewServerConnection,
                self._ebNewServerConnection,
                callbackArgs=(hostname, username),
                errbackArgs=(hostname,))


    def parseInputLine(self, line):
        if line[:1] == '/':
            special = getattr(self, 'cmd_' + line[1:].split()[0].upper(), None)
            if special is not None:
                special(line)
            else:
                self.addOutputMessage('== no such command')
        else:
            if self.channel is None:
                self.addOutputMessage('== no channel')
            else:
                self.proto.msg(self.channel, line)
                self.messageReceived(self.nickname, self.channel, line)


    def connectionMade(self):
        super(UserInterface, self).connectionMade()
        self.terminal.eraseDisplay()
        self.terminal.resetPrivateModes([privateModes.CURSOR_MODE])
        self.rootWidget = createChatRootWidget(
            self.reactor,
            self.width - 2, self.height,
            self._painter, self, self.parseInputLine)


    def connectionLost(self, reason):
        reactor.stop()


    def keystrokeReceived(self, keyID, modifier):
        self.rootWidget.keystrokeReceived(keyID, modifier)


    # IStatusModel
    def focusedChannel(self):
        return self.channel


    # IChatObserver
    def messageReceived(self, user, channel, message):
        self.addOutputMessage('[%s] <%s> %s' % (channel, user, message))


    def channelJoined(self, channel):
        self.addOutputMessage('== joined %s' % (channel,))


    def channelLeft(self, channel):
        self.addOutputMessage('== left %s' % (channel,))
