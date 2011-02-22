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

def getIdentity():
	return "pyffle_boards v0.01"

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
			messageIds = self.data.getMessagesByBoardByUsername(board,currentUser.username)
			s = None
			for msgid in messageIds:
				for msgtext in self.data.getMessagetexts(msgid):
					s = s + msgtext
			## Pass any existing message text to the editor
			editor = Editor()
			theText = editor.getText(text=s)
			confirm = self.data.util.yesnoprompt("Proceed? ")
			if confirm:
				## delete any old plans
				for msgid in messageIds:
					self.data.deleteMessage(msgid)
				## post the new plan
				sentId = self.data.createMessage(self.currentUser.username,currentUser.username,subject.strip(),theText,board=board)
				self.data.util.println("Plan posted.")
		else:
			self.data.util.println("Sorry, you are not allowed to post a plan.")

		
	

	
	def go(self, command):
		command = command.strip()
		if command == "plan":
			self.plan()
		if command == "finger":
			pass		