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
import random

def getIdentity():
	return "pyffle_cookie v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None
	
	def eventDispatched(self, event):
		pass
		

	def displayCookie(self):
		self.data.stateChange("cookie_cookiedisplaystart")			
		## first get the static cookies 
		cookies = self.data.getStaticCookies()

		## now load any added ones
		messageIds = self.data.getMessagesByBoardname("__pyffle_cookie")
		for msgid in messageIds:
			for msgtext in self.data.getMessagetexts(msgid):
				cookies.append(msgtext)
				
		## pick a random cookie and display it 
		if not cookies == None:
			if len(cookies) > 0:
				random.seed()
				cookie = random.choice(cookies)
				self.data.util.printPaged(cookie)
		self.data.stateChange("cookie_cookiedisplayend")			


	def go(self, command, args):
		if command=="justacookie":
			self.data.stateChange("cookie_justacookiestart")			
			self.displayCookie()		
			self.data.stateChange("cookie_justacookieend")			

		if command=="cookie" or command=="oreo":
			self.data.stateChange("cookie_cookiestart")			

			self.displayCookie()
			self.data.stateChange("cookie_cookieend")			
			self.data.stateChange("cookie_cookieaddstart")			
			subject = ""
			theText = self.data.util.prompt("\nEnter cookie, but no bufu.\n:")
			theText.strip()
			if not theText == "":
				self.data.stateChange("cookie_gotcookiestart")			
				self.data.util.printn("\nStoring cookie..")
				sentId = self.data.createMessage(self.currentUser.username,None,subject.strip(),theText,board="__pyffle_cookie")
				self.data.util.println("Cookie stored.\n")
				self.data.stateChange("cookie_gotcookieend")			
			else:
				self.data.stateChange("cookie_nocookiestart")			
				self.data.util.println("\nSpoilsport. No cookie for you.\n")
				self.data.stateChange("cookie_nocookieend")			
