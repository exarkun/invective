# -*- test-case-name: invective.test.test_chat -*-

"""
Twisted Words IM integration classes.

This module hooks the conversation-based callback API from L{twisted.words.im}
up to an invective output area and allows the invective input controller to
change the state of an IM account object.
"""

from twisted.words.im.basechat import ChatUI, GroupConversation


class InvectiveGroupConversation(GroupConversation):
    """
    A one-to-many conversation which displays events in an invective output
    area.
    """
    def __init__(self, group, account):
        GroupConversation.__init__(self, group, account)
        self.output = account.output


    def show(self):
        pass


    def showGroupMessage(self, sender, text, metadata=None):
        self.output.addMessage('%s/%s> %s' % (self.group.name, sender, text))


    def memberJoined(self, member):
        self.output.addMessage('%s/%s joined' % (self.group.name, member))


    def memberChangedNick(self, oldnick, newnick):
        self.output.addMessage("%s/%s is now %s/%s" % (self.group.name, oldnick, self.group.name, newnick))


    def memberLeft(self, member):
        self.output.addMessage("%s/%s left" % (self.group.name, member))


    def setTopic(self, topic, author):
        self.output.addMessage("%s/%s changed the topic to %s" % (self.group.name, author, topic))


    def setGroupMembers(self, members):
        self.output.addMessage("%s memebers: %s" % (self.group.name, ' '.join(members)))


class InvectiveChatUI(ChatUI):
    """
    L{twisted.words.im} integration class for invective.

    This primarily serves to connect the conversation classes,
    L{InvectiveConversation} and L{InvectiveGroupConversation} up to the event
    sources in L{twisted.words.im}.
    """
    def __init__(self, output):
        ChatUI.__init__(self)
        self.output = output


    def getGroupConversation(self, group, Class=InvectiveGroupConversation, stayHidden=False):
        """
        Retrieve an L{InvectiveGroupConversation} for the given group.

        @rtype: L{InvectiveGroupConversation}
        """
        return ChatUI.getGroupConversation(self, group, Class, stayHidden)
