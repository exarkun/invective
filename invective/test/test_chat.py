"""
Tests for the L{twisted.words.im} integration code in L{invective.chat}.
"""

from twisted.words.im.basesupport import AbstractAccount, AbstractPerson, AbstractGroup
from twisted.trial.unittest import TestCase

from invective.chat import InvectiveChatUI


class DummyOutput(object):
    """
    Stub message output implementation which only collects and saves messages
    added to it without trying to render them.
    """
    def __init__(self):
        self.messages = []


    def addMessage(self, message):
        self.messages.append(message)



class ChatMixin:
    """
    TestCase mixin defining a setUp method which creates L{twisted.words.im}
    account, person, and group objects for use by tests.
    """
    def setUp(self):
        """
        Create instances of several classes from twisted.words.im which are
        necessary to test the chat interface object.
        """
        self.accountName = 'account-name'
        self.autoLogin = False
        self.username = 'user name'
        self.password = 'pass word'
        self.host = 'host name'
        self.port = 12345
        self.account = AbstractAccount(
            self.accountName, self.autoLogin, self.username, self.password,
            self.host, self.port)

        self.personName = 'person name'
        self.person = AbstractPerson(self.personName, self.account)

        self.groupName = 'group name'
        self.group = AbstractGroup(self.groupName, self.account)

        self.output = DummyOutput()
        self.chat = InvectiveChatUI(self.output)



class GroupConversationTests(ChatMixin, TestCase):
    """
    Verify the behavior of L{InvectiveGroupConversation}, the one-to-many chat
    event handler.
    """
    def test_showGroupMessage(self):
        """
        Verify that new messages are properly passed on to the display layer.
        """
        message = 'hello world'
        conversation = self.chat.getGroupConversation(self.group)
        conversation.showGroupMessage(self.person.name, message, {})

        self.assertEqual(
            self.output.messages,
            ['%s/%s> %s' % (self.group.name, self.person.name, message)])
