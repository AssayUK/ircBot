#! /usr/bin/env python

import os
import ssl
import sys
import bs4
import time
import json
import socket
import threading
import subprocess
import time
import urllib2
import random
import string

inChan = False

# Setup connection
irc = socket.socket()
irc = ssl.wrap_socket(irc)

# List of currently active threads
threadlist = []

# Edit these values the server
ircServer = "<server>"
#port to connect to
ircSSLPort = <port>
# nick that the bot should take
ircNick = "<nick>"
# What the bot uses as an attention character
ircCKey = "!"
#account password to use
ircPassword ="<password>"
# List of channels to connect to
channelList = ['<channels>'
              ]

def rawSend(data):
        irc.send(data)
	print(data)
		
def ircConnect():
        irc.connect((ircServer, ircSSLPort))
	print("connect done")
		
def ircMessage(msg, channel):
        rawSend("PRIVMSG " + channel + " :" + msg + "\r\n")
        print("PRIVMSG " + channel + " :" + msg + "\r\n")
	
def ircRegister():
        rawSend("USER " + ircNick + " 0" + " *" + " :" + ircNick + "\r\n")
        time.sleep(1)
        rawSend("CAP REQ :account-notify" + "\r\n")
        time.sleep(1)
        rawSend("CAP REQ :extended-join" + "\r\n")
        time.sleep(1)
        rawSend("CAP REQ :multi-prefix" + "\r\n")
        rawSend("CAP LIST" + "\r\n")
        time.sleep(1)
        rawSend("CAP END" + "\r\n")
        time.sleep(1)
	
def ircSendNick():
        rawSend("NICK " + ircNick + "\r\n")

def Initialize():
        ircConnect()
        time.sleep(1)
        ircSendNick()
        time.sleep(1)
        ircRegister()
        time.sleep(1)
		
def channelJoin(channel, data):
     for line in data.split('\n'):
        if "JOIN" in line:
            print(line)
            foo = line.split(":")
            d,e = foo[1].split("!")
            ircMessage(("Welcome " + d  + "\r\n"), channel)
            if d[0] in string.lowercase:
                rawSend((":" + ircNick + " " + "PRIVMSG" " Chanserv voice " + channel + " " + d + "\r\n"))
        
def channelRequests(channel, data):

	# !ping to see if the bot is alive
        if ircCKey + "ping" in data:
                ircMessage("pong", channel)
                print("Pong Sent")

        # !testurl to see if a website is responding
        if ircCKey + "testurl" in data:
                hostname = data[data.find("!testurl ") + 9:]
                try:
                        hostname = hostname.strip("\r\n")
                        request = urllib2.urlopen("http://isup.me/" + hostname)
                        source = request.read()
                        if "s just you." in source:
                                ircMessage(hostname + " is up from here.", channel)
                        else:
                                ircMessage(hostname + " is down from here.", channel)
                except ValueError:
                        ircMessage("Failed to check if: " + hostname + " is up.", channel)

        # Per RFC 1149.5
        if ircCKey + "random" in data:
                ircMessage("4    ... https://xkcd.com/221/", channel)

	# because it amused me			
        if ircCKey + "hardrandom" in data:
                ircMessage(("Hard random? Yeah, soon, untill then " + str(random.random())), channel)				

Initialize()
time.sleep(5)
count = 0

while True:
        data = irc.recv(4096)
	print (data)
        # Some servers have a non-standard implementation of IRC, so we're looking for 'ING' rather than 'PING'
        if "PING" in data:
                rawSend("PONG " + data[6:24] + "\r\n")
		      				
#kludge for somones iffy server    
	if not inChan:
		count = (count + 1)
		if count == 5:
			inChan = True
		time.sleep(5)
		print("Value of inChan is " + str(inChan) + "\r\n")
		print("going round that silly loop")
		rawSend(":"  +ircNick +  " PRIVMSG " + " nickserv :identify " + ircPassword  + " \r\n")	
		for channel in channelList:
		    rawSend("JOIN " + channel + "\r\n")
                rawSend("MODE " + ircNick + " +B" + "\r\n")
		continue

		 
# Take anything sent from the server and process it for expected commands
        for channel in channelList:
			if "PRIVMSG " + channel in data:
				t = threading.Thread(target=channelRequests, args=(channel, data))
				t.daemon = True
				t.start()	
        for channel in channelList:				
            if "JOIN " + channel in data:
				channelJoin(channel, data)
        continue
