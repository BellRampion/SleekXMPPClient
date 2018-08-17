#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


class SendMsgBot2(sleekxmpp.ClientXMPP):
    #Arrays I will need later
    userMessage = ""
    recipentJID = ""


    """
    A simple XMPP client that handles sending and receiving messages.
    """


    #Should run whenever no event has been triggered recently
    def message_sender(self):
        """
        Send a message. The info is inputted earlier.
        """
        try:
            sendMessage = input("Would you like to send a message? (y/n): ")
        except ValueError as err:
            print(err)
        if sendMessage == 'y':
            self.recipient = raw_input("Enter the username (recipient@example.net) of the recipient: ")
            self.msg = raw_input("Enter a message: \n")
            self.send_message(mto=self.recipient,
                          mbody=self.msg,
                          mtype='chat')
        else:
            print("Okay, then.\n")

    def __init__(self, jid, password, recipient, message):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The message we wish to send, and the JID that
        # will receive it.
        self.recipient = recipient
        self.msg = message

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start, threaded=True)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message)


    def start(self, event):
        """
        Process the session_start event.
        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.
        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        self.get_roster()

        self.schedule('message_sender', 60, self.message_sender, args=None, kwargs=None, repeat=True)

    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.
        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        if msg['type'] in ('chat', 'normal'):
            print(msg['from'], file = open('messages.txt', 'a'))
            print(":\n", file = open('messages.txt', 'a'))
            print(msg['body'], file = open('messages.txt', 'a'))
            print(msg['from'], ":\n", msg['body'], "\n")
            try:
                reply = input("Would you like to reply? (y/n): ")
            except ValueError as err:
                print(err)
            if reply == 'y':
                userMessage = input("Enter a message: \n")
                msg.reply(userMessage).send()
                print("Message sent!\n")
            else:
                print("Okay, then.\n")
        try:
            sendMessage = input("Would you like to send a message? (y/n): ")
        except ValueError as err:
            print(err)
        if sendMessage == 'y':
            self.recipient = raw_input("Enter the username (recipient@example.net) of the recipient: ")
            self.msg = raw_input("Enter a message: \n")
            self.send_message(mto=self.recipient,
                          mbody=self.msg,
                          mtype='chat')
        else:
            print("Okay, then.\n")


if __name__ == '__main__':
    # Print welcome message
    print("XMPP CLIENT\nCREATED BY BELL\n")
    helpNeeded = input("For help, enter 'h'.")
    if (helpNeeded == 'h'):
        print("This is an XMPP client. Every minute, it will ask you if you wish to send a message. It will also ask you after every message received - but beware, for it will not wait until all unread messages have been received. Messages are also saved to a file.\n")
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-t", "--to", dest="to",
                    help="JID to send the message to")
    optp.add_option("-m", "--message", dest="message",
                    help="message to send")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    global sendMessage
    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")
    if opts.to is None:
        try:
            sendMessage = input("Would you like to send a message? (y/n): ")
        except ValueError as err:
            print(err)
        if sendMessage == 'y':
            opts.to = raw_input("Send To: ")
    if opts.message is None:
        if sendMessage == 'y':
            opts.message = raw_input("Message: ")
        elif sendMessage != 'n':
            sendMessage = input("Would you like to send a message? (y/n): ")
            if sendMessage == 'y':
                opts.message = raw_input("Message: ")

    # Setup the EchoBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = SendMsgBot2(opts.jid, opts.password, opts.to, opts.message)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # If you want to verify the SSL certificates offered by a server:
    # xmpp.ca_certs = "path/to/ca/cert"

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        print("About to connect.\n")
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
