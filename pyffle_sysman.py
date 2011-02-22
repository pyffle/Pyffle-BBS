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

class PyffleSysman:

	session = None
	data = None
	currentUser = None
	uucpboards = ["uuhec.hecnet"]
	uucpfeeds = ["b4bbs"]
	nntpfeeds = ["news.eternal-september.org"]
	nntpboards = ["alt.test"]
	VERSION = "Pyffle sendnews v0.01"
	doNntp = False
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
					value = str(lineElements[1]).strip()
					rv[key] = value
				else:
					## body, append it + \n 
					payload = payload + e + "\n"
					
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
	
	def formatNntpDate(self, date):
		## Fri, 19 Nov 82 16:14:55 GMT
		rv = date.strftime("%a, %d %b %Y %H:%M:%S %Z")		
		return rv
		
	def displayMessage(self,instance,showPayload=False):
		## Sends the supplied message
		self.data.util.debugln("NEWS SEND")

		fromhdr = instance.fromname
		tohdr = instance.toname		
		subjhdr = instance.subject
		payload = ""
		for msgtext in self.data.getMessagetexts(instance.id):
			payload = payload + msgtext
		
		rv = ""
		rv = rv 
		rv = rv + "  **** ID: <%s> " % str(instance.id)
		rv = rv + ("%s" % str(fromhdr))[0:15]
		rv = rv + (" => %s" % str(tohdr))[0:15]
		rv = rv + ("| S=%s" % str(subjhdr))[0:20]
		rv = rv + ("| D=%s" % str(instance.sentdate))[0:20]
		print rv[0:80]
		if showPayload:
			print payload

	def listmsgs(self, boardname=None,unread=False):
		if boardname == None:
			boards = self.data.getBoards()	
		for board in boards:
			print "---- BOARD: " + board.name

			msgids = self.data.getMessagesByBoardid(board.id)
			for msgid in msgids:
				msg = self.data.getMessage(msgid)
				self.displayMessage(msg,showPayload=False)
		return
	
	def listusers(self,username=None):
		users = []
		if username == None:
			users = self.data.getUsers()	

		self.data.util.println("\nUserlist @ %n, " + str(users.count()) + " total\n")
		for user in users:
			username = user.username
			identity = user.fullidentity
			lastlogin = user.datefastlogin
			lastlogin = self.data.util.formatDateString(lastlogin)
			comment = user.comment
			self.data.util.println("{0:10} | ".format(username) + "{0:25} | ".format(identity) + "{0:13} | ".format(lastlogin) + comment)
		self.data.util.println("")
					
	def go(self,cmd):	
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
			
		if cmd == "listmsgs":
			self.listmsgs()

		if cmd == "listusers":
			self.listusers()

### main program starts here
args = sys.argv

cmd = None
if (len(args) == 2):
	cmd = args[1]
else:
	print "weird args"

print "|%s|" % str(cmd)
if not cmd == None:		
	pyffleSysman = PyffleSysman()
	print "Executing %s" % cmd
	pyffleSysman.go(cmd)
	