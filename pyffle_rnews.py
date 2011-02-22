#! /usr/bin/python
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
import pyffle_mail
from pyffle_util import PyffleUtil
from pyffle_static import PyffleStatic
from datetime import datetime
import sys
import getpass
import os
import copy
import email
import warnings

class PyffleRnews:

	session = None
	data = None
	currentUser = None
	
	def parseNews(self,s):
		rv = {}
		elements = s.split("\n")
		## header first...
		rv['From'] = ""
		rv['Subject'] = ""
		## now the body
		payload = ""
		header = True
		seenNonBlank = False
		for e in elements:
			e = e.strip()
			if e == "":
				## Blank line
				## Are reading the header?
				if header:
					## yes, we are, that's the end of the header, ignore input 
					## and start parsing the body, unless we've only seen blanks
					## upto now
					if seenNonBlank:
						header = False
				else:
					## reading the body, append blank line to payload
					payload = payload + "\n"
			else:
				## non-blank line
				seenNonBlank = True
				if header:
					## header line
					lineElements = e.split(":")
					key = str(lineElements[0]).strip()
					if len(lineElements) >= 2:
						value = ""
						i = 0
						for element in lineElements[1:]:
							## don't add a : for the first element, do for others
							if i == 0:
								pass
							else:
								value = value + ":"
							i = i + 1
							value = value + str(element).strip()
						rv[key] = value
				else:
					## body, append it + \n 
					payload = payload + self.data.util.printable(e) + "\n"
					
		rv['payload'] = payload
		return rv
				
		
		
		
	## Clears the message base and writes two messages, dumps them to screen,
	## deletes them
	def parseIncomingAddress(self,toAddress):
		username,hostname = toAddress.lower().split("@")
		return username,hostname
		
	def incomingAddressIsLocal(self,toAddress):
		aliases = [self.data.static.options["node"].strip().lower()]
		for alias in self.data.static.options["alias"].split(","):
			aliases.append(alias.strip().lower())
		username,hostname = self.parseIncomingAddress(toAddress.strip().lower())
		if hostname in aliases:
			return True
		else:
			return False
			
	def debugMessageTest(self):
		self.data.clearMessages()
		msg1 = self.data.createMessage("fooble","sampsa","Test from py","Hello earth")
		msg2 = self.data.createMessage("foo@bar.com","sampsa","Test to outside","Hello sky")
		self.data.dumpMessages()
		self.data.deleteMessage(msg1)
		self.data.deleteMessage(msg2)

	def go(self):	
		## Initialise the main controller, load static file
		self.data = PyffleData()
		self.data.toolMode = True 	## Turn on Tool Mode so that we override security restrictions
		static = PyffleStatic()		## FIXME read this from a env var or something
		static.parse("/pyffle/static")
		self.data.static = static

		## Setup the DB connection
		Session = sessionmaker()
		engine = create_engine(static.options["pyffle.dburl"], echo=False) ### FIXME pull this out of static
		Session.configure(bind=engine)	
		self.session = Session()
		self.data.session = self.session
		
		## Setup up the utility class
		util = PyffleUtil()
		util.data = self.data
		self.data.util = util
		self.data.toolMode = True	
		## Load the MTA plugins
		mtalist = [["pyffle_mta_uucp","Pyffle UUCP","UUCP MTA for Pyffle"]]
		self.data.loadMtaList(mtalist)
			
		## parse the incoming message
		msgString = sys.stdin.read()
		rfcMsg = self.parseNews(msgString)
		payload = rfcMsg['payload']		
		newsgrouphdr = rfcMsg['Newsgroups']
		newsgroups = []
		if newsgrouphdr.count(",") > 0:
			## multiple groups specified
			for e in newsgrouphdr.split(","):
				newsgroups.append(e.strip())
		else:
			newsgroups = [newsgrouphdr]

		for newsgroup in newsgroups:		
			newsgroup = newsgroup.lower()
			destBoard = self.data.getBoardByExternalname(newsgroup)
			if not destBoard == None:
				internalName = destBoard.name
				msgid = self.data.createMessage(rfcMsg['From'],None,rfcMsg['Subject'],payload,board=internalName)		
				self.data.setMessageRead(msgid) ## mark it as read so we don't export it again
				self.data.logEntry(self.data.LOGINFO,"IMPORT/MESSAGE/NEWS",str("RNEWS"),"Received news on %s from %s" % (str(destBoard.externalname),str(rfcMsg['From'])))		
			else: 
				print "We don't carry " + newsgroup
		



def runmain():
	### main program starts here
	args = sys.argv
	
	pyffleRnews = PyffleRnews()
	pyffleRnews.go()
	
	
import cProfile
cProfile.run("runmain()","/pyffle/data/rnews.profile")
	