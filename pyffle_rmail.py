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

class PyffleRmail:

	session = None
	data = None
	currentUser = None
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

	def go(self,finalDestination):	
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
		
		## Load the MTA plugins
		mtalist = [["pyffle_mta_uucp","Pyffle UUCP","UUCP MTA for Pyffle"]]
		self.data.loadMtaList(mtalist)

		## parse the incoming message
		msgString = sys.stdin.read()
		rfcMsg = email.message_from_string(msgString)
		payload = rfcMsg.get_payload()		
		
		toAddress = finalDestination

		## is this a local message?
		if self.incomingAddressIsLocal(toAddress):
			toname,hostname = self.parseIncomingAddress(toAddress)
			## Ask an MTA to parse the incoming address
			if (not toname == "") and (not toname == None):
				##print "F=%s T=%s S=%s\n" % (rfcMsg['From'],toname,rfcMsg['Subject'])
				## Store the message
				self.data.createMessage(rfcMsg['From'],toname,rfcMsg['Subject'],payload)		
				self.data.logEntry(self.data.LOGINFO,"IMPORT/MESSAGE/RMAIL",str(toname),"Received mail for %s from %s" % (str(toname),str(rfcMsg['From'])))		

		else: 
			pass
			print "Sending to external rmail"
			## Pass to external rmail
			with warnings.catch_warnings(record=True) as warn:
				## FIXME CRITICAL: need to sanitize the To header here...Shell injection
				rmail = self.data.static.options["pyffle.extrmail"] + " " + finalDestination
				mailin, mailout = os.popen2(rmail)
				mailin.write(msgString)
				mailout.close()
				mailin.close()
			
	
		
### Main program



args = sys.argv

if len(args) == 2:
	pyffleRmail = PyffleRmail()
	pyffleRmail.go(args[1])
else:
	print "Invalid command line arguments. Usage: pyffle_rmail <final destination address>"
	