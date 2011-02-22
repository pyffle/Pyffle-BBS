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
# Import the email modules we'll need
from email.mime.text import MIMEText

import warnings


		
def getIdentity():
	return "pyffle_mta_uucp v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleMta:
	currentUser = None
	data = None	 

	def matchIncomingAddress(self,s):
		## Returns true if we can process this kind of address
		if s.find("!") > 0:
			return True
		else:
			return False

	def getName(self):
		return "Pyffle UUCP MTA"
		
	def parseIncomingAddress(self,s):
		## Returns tuple with the local user and system specified by this incoming address
		elements = s.split("!")
		username = elements[len(elements)-1]
		username = username.strip()
		system = elements[len(elements)-2]
		system = system.strip()
		return username,system
	
	def processAddress(self,s):
		## Often you get an address like foo@bar.com (Foo Bar) - we want to 
		## Break the address down by spaces
		realaddress = ""
		for e in s.split(" "):
			if (e.find("!")) > 0 or (e.find("@") > 0):
				## this is the actual address bit
				realaddress = e
				break
		return realaddress

		
	def matchAddress(self,s):
		## Returns true if we can process this kind of address
		if (s.find("!")) > 0 or (s.find("@") > 0):
			return True
		else:
			return False

	def sendMessage(self,instance):
		## Sends the supplied message
		self.data.util.debugln("UUCP SEND")
		
		sender = self.data.getUser(instance.fromname.strip())
		
		username = instance.fromname.strip()
		fromaddress = "%s@%s" % (instance.fromname.strip(),self.data.static.options['node'])
		fromhdr = "%s <%s>" % (sender.fullidentity,fromaddress)
		tohdr 	= self.processAddress(instance.toname.strip())
		subjhdr = instance.subject
		payload = ""
		for msgtext in self.data.getMessagetexts(instance.id):
			payload = payload + msgtext
		
		
		# Create a text/plain message
		msg = MIMEText(payload)
		
		# me == the sender's email address
		# you == the recipient's email address
		msg.set_unixfrom("From " + fromhdr)
		msg['From'] = fromhdr
		msg['To'] = tohdr
		msg['Subject'] = subjhdr
		msg['X-Mailer'] = "%s (%s)" % (self.getName(), getIdentity())
		msg['X-Pyffle-Version'] = "%s" % (getIdentity())
		 

		with warnings.catch_warnings(record=True) as warn:
			## FIXME CRITICAL: need to sanitize the To header here...Shell injection
			sendmail = self.data.static.options["pyffle.sendmail"] + " " + tohdr
			mailin, mailout = os.popen2(sendmail)
			mailin.write(msg.as_string(True))
			mailout.close()
			mailin.close()

		self.data.util.println("Accepted for delivery (%s)\n" % (self.getName()))
		self.data.logEntry(self.data.LOGINFO,"DELIVER/MESSAGE/UUCP",str(username),"Sent mail to %s for %s" % (str(tohdr),str(username)))		
		return		

	