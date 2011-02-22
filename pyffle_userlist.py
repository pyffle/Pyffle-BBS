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
	return "pyffle_userlist v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:

	def eventDispatched(self, event):
		pass

	def listUsers(self):
		## val     10 | val chiswell       25    | 23-Oct-10   13 | No comment..
		users = self.data.getUsers()
		
		## Userlist @ waffle.uuhec.net, 23 total

		self.data.util.println("\nUserlist @ %n, " + str(users.count()) + " total\n")
		for user in users:
			username = user.username
			identity = user.fullidentity
			lastlogin = user.datefastlogin
			lastlogin = self.data.util.formatDateString(lastlogin)
			comment = user.comment
			self.data.util.println("{0:10} | ".format(username) + "{0:25} | ".format(identity) + "{0:13} | ".format(lastlogin) + comment)
		self.data.util.println("")
		
		
			
	currentUser = None
	data = None
	
	def go(self, command, args):
		if command == "users":
			self.listUsers()
			
