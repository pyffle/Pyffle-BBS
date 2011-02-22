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
import pyffle_editor
from datetime import datetime
import sys
import getpass
import os
import tempfile

def getIdentity():
	return "pyffle_inspector v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None

	def eventDispatched(self, event):
		pass
		
	def indent(self,n):
		for i in range(1,n):
			self.data.util.printn("  ")

	def printAce(self, aces,indent):
		self.data.util.printn("%s=>%s " % (aces[0], aces[1]))
			
	def	printJoins(self,username,indent):
		self.indent(indent)
		self.data.util.println("^JOIN^ %s" % (str(self.data.getJoinedBoardids(username=username))))
		
	def printAcl(self, aclid, indent):
		msgAcl = self.data.getAcl(aclid)
		self.indent(indent)
		self.data.util.println("^ACL^ %s (%s)" % (msgAcl.id,msgAcl.description))

		grants = self.data.getAces(aclid,"GRANT")
		denies = self.data.getAces(aclid,"DENY")
		
		self.indent(indent)
		self.data.util.printn("  ^GRANT^: ")
		
		for grant in grants:
			self.printAce(grant,indent+1)
		self.data.util.println(" ")
		
		self.indent(indent)
		self.data.util.printn("  ^DENY^: ")
		for deny in denies:
			self.printAce(deny,indent+1)
		self.data.util.println(" ")

	def printMsg(self, msgid, indent):
		msg = self.data.getMessage(msgid)
		self.indent(indent)
		board = self.data.getBoard(msg.boardid)
		self.data.util.println("^MSG^ %s %s -> %s (%s) in %s" % (msg.id,msg.fromname,msg.toname,msg.subject,board.name))
		aclid = msg.aclid
		self.printAcl(aclid,indent + 1)
		
		
	def printUser(self, username):
		self.data.util.cls()
		user = self.data.getUser(username)
		self.data.util.println("^USER^ " + username)
		self.printAcl(user.aclid, 2)
		self.printJoins(username, 2)
		msgids = self.data.getMessagesAuthoredByUser(username)
		for msgid in msgids:
			self.printMsg(msgid, 2)
		
			
	def printBoard(self, boardname):
		self.data.util.cls()
		board = self.data.getBoardByName(boardname)
		self.data.util.println("^BOARD^ " + boardname)
		self.printAcl(board.aclid, 2)
		msgids = self.data.getMessagesByBoardname(boardname)
		for msgid in msgids:
			self.printMsg(msgid, 2)
		
	def go(self, command, args):
		if command == "iuser":
			self.data.stateChange("inspector_iuserstart")	
			username = args[1].strip()
			self.printUser(username)
			self.data.stateChange("inspector_iuserend")	
		
		if command == "iboard":
			self.data.stateChange("inspector_iboardstart")	
			name = args[1].strip()
			self.printBoard(name)
			self.data.stateChange("inspector_iboardend")	
