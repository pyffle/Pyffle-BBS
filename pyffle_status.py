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
	
	currentUser = None
	data = None

	def eventDispatched(self, event):
		pass


	def showStatus(self):
		self.data.util.printPaged(self.data.util.texts["TEXT"]["status"])
	
	def setPassword(self):
		## FIXME check old
		self.data.util.printn("New Password: ")
		password1 = self.data.util.readPassword() 
		self.data.util.printn("Verify:       ")
		password2 = self.data.util.readPassword()
		password1 = password1.strip()
		password2 = password2.strip()
		 
		if password1 == password2:
			## FIXME UPDATE really
			self.data.util.println("\nPassword updated.")
		else:
			self.data.util.println("\nERROR: Apple != Orange - Passwords don't match")
		self.data.setPassword(password1)


	def status(self):	
		userQuits = False
		while not userQuits:
			self.data.util.cls()
			self.showStatus()
			choice = self.data.util.prompt("change ^E^ditor ^L^evel ^N^ame ^P^assword ^T^erminal   ^X^ Exit? ")
			choice = choice.lower()
			validChoice = False
			if choice == "p":
				self.setPassword()
				validChoice = True
				break
			if choice == "e":
				self.data.util.prompt("\nNo other editors available.")
				validChoice = True
			if choice == "l" or choice == "n":
				self.data.util.prompt("\nNot authorizado. Quo vadis?")
				validChoice = True
			if choice == "t":
				self.data.util.prompt("\nNo other terminals available.")
				validChoice = True

			if choice == "x":
				break
				
			if not validChoice:
				self.data.util.printraw("\n'%s' is not a valid option here, dude." % choice)
				
			
	def go(self, command, args):
		if command == "status":
			self.status()
			
