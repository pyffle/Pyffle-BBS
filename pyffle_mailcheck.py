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

def getIdentity():
	return "pyffle_mailcheck v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

## Catches event "mainmenupromptstart" and does a mail check

class PyffleModule(pyffle_module.PyffleModule):
	currentUser = None
	data = None

	def mailcheck(self):
		self.data.stateChange("mailcheck_start")								
		if not self.data.getNewMessages() == []:
			self.data.stateChange("mailcheck_foundstart")
			self.data.util.println("\nYou have new mail")
			self.data.stateChange("mailcheck_foundend")	
		self.data.stateChange("mailcheck_end")

		
	def eventDispatched(self, event):
		if event[0] == "mainmenupromptstart":
			self.mailcheck()
		