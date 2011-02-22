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
	return "pyffle_finger v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None
		
	def eventDispatched(self, event):
		pass

	def displayMessage(self,msgid):
		instance = self.data.getMessage(msgid) 
		for msgtext in self.data.getMessagetexts(msgid):
			self.data.util.println(msgtext)
		self.data.util.printraw(" ")

		
		
	def plan(self):	
		board = self.data.getBoardByName('__pyffle_plan')
		if self.data.srmcheck(board.aclid,self.currentUser.username,"POST",minlevel=board.minpostlevel):
			## Retrieve the existing plan, if any
			messageIds = self.data.getMessagesByBoardByUsername(board,self.currentUser.username)
			s = ""
			if not messageIds == None:
				for msgid in messageIds:
					for msgtext in self.data.getMessagetexts(msgid):
						s = s + str(msgtext)
			## Pass any existing message text to the editor
			editor = Editor()
			theText = editor.getText(text=s)
			confirm = self.data.util.yesnoprompt("Proceed? ")
			if confirm:
				## delete any old plans
				for msgid in messageIds:
					self.data.deleteMessage(msgid)
				## post the new plan
				sentId = self.data.createMessage(self.currentUser.username,self.currentUser.username,"",theText,board=board.name)
				self.data.util.println("Plan posted.")
		else:
			self.data.util.println("Sorry, you are not permitted to post a plan.")

	def finger(self):
		targetUser = self.data.util.prompt("User: ")
		targetUser = targetUser.strip()
		board = self.data.getBoardByName('__pyffle_plan')
		if not self.data.srmcheck(board.aclid,self.currentUser.username,"READ",minlevel=board.minpostlevel):
			self.data.util.println("Sorry, you are not permitted to FINGER users.")
			return

		messageIds = self.data.getMessagesByBoardByUsername(board,targetUser)
		s = ""
		if not messageIds == None:
			for msgid in messageIds:
				for msgtext in self.data.getMessagetexts(msgid):
					s = s + msgtext
		## FIXME put other finger stuff here as well
		if s == "":
			self.data.util.println("User has no plan.")
		else:
			self.data.util.println("Plan:")
			self.data.util.printPagedRaw(s)
			
		return
	
	def go(self, command, args):
		command = command.strip()
		if command == "plan":
			self.plan()
		if command == "finger":
			self.finger()		