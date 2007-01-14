# -*- test-case-name: invective.test -*-

"""
Controller classes for interacting with an IRC server.
"""

from twisted.words.protocols.irc import IRCClient as BaseIRCClient


class IRCClient(BaseIRCClient):
    """
    Simple IRC client protocol class which passes events off to another layer
    in a somewhat structured manner and exposes an API for sending events to an
    IRC server.
    """
    performLogin = False

    def __init__(self, observer):
        self.observer = observer


    def privmsg(self, user, channel, message):
        self.observer.messageReceived(user, channel, message)


    def joined(self, channel):
        self.observer.channelJoined(channel)


    def left(self, channel):
        self.observer.channelLeft(channel)



__all__ = ['IRCClient']

