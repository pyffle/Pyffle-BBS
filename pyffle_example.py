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

## Returns an identity string describing out module
def getIdentity():
	return "pyffle_example v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	rv = True
	if version == "ReallyBadVersion":
		rv = False
	return rv



class PyffleModule(pyffle_module.PyffleModule):

	def eventDispatched(self, event):
		## We react to whenever the main menu prompt is about to be
		## displayed and say hello
		if event[0] == "mainmenupromptstart":
			self.data.util.debugln("\n^Hello^\n")
		
	def go(self, command, args):
		self.data.stateChange("example_start")
		## Get our username
		username = self.data.currentUser.username
		
		## Display when this was previously accessed, if at all
		self.data.stateChange("example_previousaccessstart")
		previousAccess = self.data.pluginReadSystem("example_previousaccess")  ## True == pluginsystem table
		if not previousAccess == None:
			self.data.util.println("Previously access at %s" % (previousAccess))
		self.data.stateChange("example_previousaccessend")
				
		## Display previous feelings, if any:
		self.data.stateChange("example_oldstart")
		oldFeelings = self.data.pluginReadUser(username,"example_userFeelings")  ## False == pluginuser table
		if not oldFeelings == None:
			self.data.util.println("You felt %s previously" % (oldFeelings))
		self.data.stateChange("example_oldend")
					
		## Ask the user a question
		self.data.stateChange("example_promptstart")
		userFeelings = self.data.util.prompt("How are you today? ")
		self.data.stateChange("example_promptend")
		
		## Store some data
		self.data.pluginWriteUser(username,"example_userFeelings",userFeelings)
		self.data.pluginWriteSystem("example_previousaccess",str(datetime.now()))
		
		self.data.stateChange("example_end")		
		