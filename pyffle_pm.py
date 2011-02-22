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

def getIdentity():
	return "pyffle_online v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None
		
		
	def eventDispatched(self, event):
		if event[0] == "mainmenuloopstart":
			self.data.stateChange("pmcheckstart")
			self.printAllPms()
			self.data.stateChange("pmcheckend")
			
			
	## lists the sessions in the currentlyon table
	def isOnline(self,username):
		rv = False
		entries = self.data.getCurrentlyonEntries() 
		for entry in entries:
			if username == entry.username:
				rv = True
				break
		return rv

	def pm(self,target):
		if self.isOnline(target):
			message = self.data.util.prompt("Msg> ")
			msgid = self.data.createMessage(self.data.currentUser.username,target,message,"<PM>",board='__pyffle_pm')
			msgAcl = self.data.getMessage(msgid)
			self.data.grant(msgAcl,target,"READ")
			self.data.grant(msgAcl,target,"DELETE")
			 
		else:
			self.data.util.println("User not online. Try an email?")

	def printAllPms(self):
		pmBoard = self.data.getBoardByName("__pyffle_pm")
		msgids = self.data.getMessagesByBoardByToUsername(pmBoard,self.data.currentUser.username)
		for msgid in msgids:
			msg = self.data.getMessage(msgid)
			self.data.util.prompt("^Incoming PM^ - Press Return to read..")
			self.data.util.println("\n^PM=>^   " + msg.fromname + ": " + msg.subject + "\n")
			self.data.toolMode = True
			self.data.deleteMessage(msgid)
			self.data.toolMode = False			  
			
			
	def go(self, command, args):
		command = command.strip()
		if command == "_dump":
##			self.data._dumpMessages()
			pass

		if command == "pm":
			destination = None
			if (len(args) >= 2):
				destination = args[1]
			else:
				destination = self.data.util.prompt("Send to: ")
		
			self.pm(destination.strip())
		if command == "!check_pms":
			self.printAllPms()
			