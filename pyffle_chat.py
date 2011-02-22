###
###    This file is part of Pyffle BBS.
###
###    Pyffle BBS is free software: you can redistribute it and/or modify
###    it under the terms of the GNU General Public License as published by
###    the Free Software Foundation, either version 3 of the License, or
###    (at your option) any later version.
###
###    Pyffle BBS is distributed in the hope that it will be useful,
###    but WITHOUT ANY WARRANTY; without even the implied warranty of
###    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
###    GNU General Public License for more details.
###
###    You should have received a copy of the GNU General Public License
###    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
###
###


## Models for SqlAlchemy version 6
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref
from sqlalchemy import *
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.orm import sessionmaker
from pyffle_tables import *
from pyffle_data import *
from pyffle_editor import Editor
from datetime import datetime
import sys
import getpass
import os
import tempfile
import pyffle_module
import copy
import time
from sqlalchemy.orm import scoped_session, sessionmaker

from threading import Thread
## Returns an identity string describing out module
def getIdentity():
	return "pyffle_example v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	rv = True
	if version == "ReallyBadVersion":
		rv = False
	return rv

class chatReader(Thread):
	data = None
	parentData = None ## For dispatching events
	lastCheck = None
	chatBoard = None
	newmsgids = None
	foundNew = False
	localSession = None
	username = None
	stopLoop = False
	def __init__ (self,data):
		Thread.__init__(self)
		## make a clone of our data and give it a new DB session
		## this is ok as we don't persist any data anyway...
		self.data = copy.copy(data)
		self.parentData = data
		self.username = data.currentUser.username
		self.data.session = self.data.getLocalSession()
		self.lastCheck = datetime.now()	
		self.chatBoard = self.data.getBoardByName("__pyffle_chat")
	
	def stop(self):
		self.stopLoop = True
		
	def run(self):
		# get any messages since the last check
		while not self.stopLoop:
			time.sleep(0.05)	
			hello = None
			self.data.session.rollback()		## this is so stupid FIXME
			self.newmsgids = self.data.getMessagesSince(self.chatBoard,self.lastCheck,checkSrm = False)
			self.foundNew = False
			for msgid in self.newmsgids:
				msg = self.data.getMessage(msgid)
				if not msg.fromname == self.username:
					self.foundNew = True
					msgtext = []
					while msgtext == []:  ## due to DB delays, the msg text might not be stored yet whilst the messge is..
						msgtext = self.data.getMessagetexts(msgid)
					sys.stdout.write("\n\x1b[7m%s\x1b[0m: %s\n" % (msg.fromname,msgtext[0]))
					self.lastCheck = datetime.now()	
	    
class PyffleModule(pyffle_module.PyffleModule):

	def printChatPrompt(self):
		pass	
	def eventDispatched(self, event):
		## We react to whenever the main menu prompt is about to be
		## displayed and send any chat invites that might be pending (FIXME implement)
		if event[0] == "userlogon":
			self.data.util.println("\n** %s has logged onto the system" % event[1])
		if event[0] == "chat_foundnew":	
			pass
				
	def sendMessage(self, username,msg):
	
		self.data.createMessage(username,None,"chat messge",msg,board='__pyffle_chat')	
		
	def go(self, command, args):
		self.data.stateChange("chat_start")
		self.data.util.println("\n\nPyffle Chat - ^/quit^ to quit\n\n")
		## create the reader thread
		reader = chatReader(self.data)
		reader.start()
		
		## Get our username
		username = self.data.currentUser.username
		
		## Loop, asking for messages to post and posting them until user inputs /quit
		userQuits = False
		self.data.stateChange("chat_loopstart")
		self.sendMessage(username,"%s has joined" % username)
		while not userQuits:
			try:
				self.printChatPrompt()
				self.data.stateChange("chat_promptstart")
				choice = self.data.util.prompt("")
				self.data.stateChange("chat_promptend")
				choice = choice.strip()
				if not choice == "":
					if choice.lower() == "/quit":
						userQuits = True
						self.data.stateChange("chat_userquits")
						break
					else:
						## User typed a message
						self.data.stateChange("chat_msgsendstart")
						self.sendMessage(username,choice)
						self.data.stateChange("chat_msgsendend")
			except:
				pass
		self.data.stateChange("chat_loopend")
		reader.stop()
		self.sendMessage(username,"%s has left" % username)
		time.sleep(0.20)
		
		self.data.stateChange("chat_end")
