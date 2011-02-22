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
	return "pyffle_boardadmin v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None

	def eventDispatched(self, event):
		pass
		
	
	
	def dropBoard(self):
		self.data.util.println(getIdentity() + "\n")
		self.data.stateChange("boardadmin_dropboardstart")
		self.data.util.println("Dropping board...")
		self.data.stateChange("boardadmin_dropboardpromptstart")
		name = self.data.util.prompt("Board Name: ")
		self.data.stateChange("boardadmin_dropboardpromptend")
		self.data.stateChange("boardadmin_dropboardconfirmstart")
		confirm = self.data.util.yesnoprompt("Proceed? ")
		if confirm:
			self.data.stateChange("boardadmin_dropboarddeletestart")
			self.data.util.printn("Dropping board...")
			self.data.deleteBoardByBoardname(name)
			self.data.util.println("Board dropped.")
			self.data.stateChange("boardadmin_dropboarddeleteend")
		self.data.stateChange("boardadmin_dropboardconfirmend")
		self.data.stateChange("boardadmin_dropboardend")

		
	def createBoard(self):	
		self.data.util.println(getIdentity() + "\n")

		self.data.stateChange("boardadmin_creatboardpromptsstart")
		self.data.util.println("Creating board...")
		name 		= 	self.data.util.prompt("Board Name:          ")
		description = 	self.data.util.prompt("Description:			")
		owner 		= 	self.data.util.prompt("Owner				")
		externalname = 	self.data.util.prompt("External name		")
		minreadlevel = 	self.data.util.prompt("Minreadlevel			")
		minpostlevel = 	self.data.util.prompt("Minpostlvel			")
		minoplevel	 = 	self.data.util.prompt("Min OP Level:		")
		self.data.stateChange("boardadmin_creatboardpromptsend")
		
		self.data.stateChange("boardadmin_creatboardconfirmstart")		
		confirm = self.data.util.yesnoprompt("Proceed? ")
		if confirm:
			self.data.stateChange("boardadmin_creatboardaddstart")		
			self.data.util.printn("\nAdding board...")
			self.data.createBoard(name, 		
			description,
			owner, 		
			externalname,
			minreadlevel,
			minpostlevel,
			minoplevel)
			self.data.util.println("Board added.")
			self.data.stateChange("boardadmin_creatboardaddend")
		else:
			self.data.stateChange("boardadmin_creatboardcancel")
		self.data.stateChange("boardadmin_creatboardconfirmend")
		self.data.stateChange("boardadmin_creatboardend")
		
	def go(self, command, args):
		self.data.stateChange("boardadmin_start")
		command = command.strip()
		if command == "create":
			self.data.stateChange("boardadmin_createstart")
			if self.data.srmcheck(self.currentUser.aclid,self.currentUser.username,"CREATEBOARD"):
				self.createBoard()
			else:
				self.data.stateChange("boardadmin_createboardsecurityfailstart")
				self.data.util.println("You do not have the permission to add boards.")
				self.data.stateChange("boardadmin_createboardsecurityfailend")
			self.data.stateChange("boardadmin_createend")
			
		if command == "drop":
			self.data.stateChange("boardadmin_dropstart")
			if self.data.srmcheck(self.currentUser.aclid,self.currentUser.username,"DROPBOARD"):
				self.dropBoard()
			else:
				self.data.stateChange("boardadmin_dropboardsecurityfailstart")
				self.data.util.println("You do not have the permission to drop boards.")
				self.data.stateChange("boardadmin_dropboardsecurityfailend")
			self.data.stateChange("boardadmin_dropend")
