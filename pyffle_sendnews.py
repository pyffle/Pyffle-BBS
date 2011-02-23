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

class PyffleSendnews:

## USER CONFIGURE STARTS HERE
	uucpboards = ["uuhec.hecnet"]
	uucpfeeds = ["b4bbs"]
	nntpfeeds = ["news.eternal-september.org"]
	nntpboards = ["alt.test"]
## USER CONFIGURE ENDS HERE

	session = None
	data = None
	currentUser = None
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
				
		
		
	
	def formatNntpDate(self, date):
		## Fri, 19 Nov 82 16:14:55 GMT
		rv = date.strftime("%a, %d %b %Y %H:%M:%S %Z")		
		return rv
		
	def sendMessage(self,instance, feeds):
		## Sends the supplied message
		self.data.util.debugln("NEWS SEND")

		fromhdr = ""		
		if not instance.fromname.strip().count("@"):
			## local user
			fromaddress = "%s@%s" % (instance.fromname.strip(),self.data.static.options['node'])
			## FIXME add user's name here
##			fromhdr = "%s <%s>" % (sender.fullidentity,fromaddress)
			fromhdr = fromaddress
		else:
			fromhdr = instance.fromname.strip()
		subjhdr = instance.subject
		payload = ""
		for msgtext in self.data.getMessagetexts(instance.id):
			payload = payload + msgtext

		board = self.data.getBoard(instance.boardid)
		newsgroups = board.externalname
		
		rv = ""
		rv = rv + "Newsgroups: " + newsgroups
		rv = rv + "\nFrom: " + fromhdr
		rv = rv + "\nSubject: " + subjhdr
		rv = rv + "\nDate: " + str(self.formatNntpDate(instance.sentdate))
		rv = rv + "\nMessage-ID: <%s>" % (str(instance.id) + "@" + self.data.static.options["node"])
		
		rv = rv + "\nPath: " + self.data.static.options["uucpname"]
		rv = rv + "\n\n"
		rv = rv + payload
		
		rv = rv + "\n--- " + self.VERSION
		
		print "=== MESSAGE ==="
		print rv
		print "=== MESSAGE ==="
		## call uux on each feed
		print "Sending message " + str(instance.id)
		self.data.setMessageRead(instance.id) ## mark it as read so we don't export it again

		for hostname in feeds:		
			print "  Fed to " + hostname
			## mark message as read (==sent)
			with warnings.catch_warnings(record=True) as warn:
				cmdline = "uux -z -p " + hostname + "!rnews"
				if self.doNntp:
					cmdline = "./nntpout.py " + hostname
				mailin = os.popen(cmdline,"w")
				mailin.write(rv)
				mailin.close()


		

	def go(self,nntp):	
		self.doNntp = nntp
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
			
		## pick the boards to loop and feeds
		boards = self.uucpboards
		feeds = self.uucpfeeds
		if nntp:
			boards = self.nntpboards
			feeds = self.nntpfeeds
	
		for boardextname in boards:
			board = self.data.getBoardByExternalname(boardextname)
			print "*** Processing " + board.externalname
			msgids = self.data.getNewMessagesAllUsers(boardname=board.name)
			for msgid in msgids:
				msg = self.data.getMessage(msgid)
				self.sendMessage(msg,feeds)
		return
					


### main program starts here
args = sys.argv

nntp = False













print len(args)
if (len(args) == 2):
	if args[1] == "nntp":
		print "Doing nntp"
		nntp = True
	else:
		print "weird args"
pyffleSendnews = PyffleSendnews()
pyffleSendnews.go(nntp)
	