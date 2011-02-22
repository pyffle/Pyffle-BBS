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
		pass
	
	## lists the sessions in the currentlyon table
	def online(self):
		entries = self.data.getCurrentlyonEntries() 
		self.data.util.println("")
		self.data.util.println("{0:<15}  ".format("User") + " {0:<15}   ".format("Since")  + " {0:<15}   ".format("Origin"))
		self.data.util.println("----------------+------------------+------------------")
		for entry in entries:
			self.data.util.println("{0:<15} | ".format(entry.username) + "{0:<15} | ".format(self.data.util.formatDateTimeString(entry.dateon)) + "{0:<30}  ".format(entry.origin))

		self.data.util.printraw(" ")

	def go(self, command, args):
		command = command.strip()
		if command == "online":
			self.online()
		if command == "!reset":
			self.data.resetCurrentlyOn()
			self.data.clearMessages()