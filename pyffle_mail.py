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

def getIdentity():
	return "pyffle_mail v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None	 

	def eventDispatched(self, event):
		pass

	def offerPurge(self,msgids):
		self.data.stateChange("mail_offerpurgestart")
		if not msgids == []:
			self.data.stateChange("mail_offerpurgepromptstart")
			confirm = self.data.util.yesnoprompt("\nDelete messages? ")
			self.data.stateChange("mail_offerpurgepromptend")
			if confirm:
				if len(msgids) > 5:
					self.data.stateChange("mail_offerpurgeconfirmstart")
					confirm = self.data.util.yesnoprompt("Delete ALL %s messages?" % (str(len(msgids))))
					self.data.stateChange("mail_offerpurgeconfirmend")
				if confirm:
					self.data.stateChange("mail_purgingstart")
					for msgid in msgids:
						msg = self.data.getMessage(msgid)
						self.data.util.println("Deleting message #%s from %s" % (str(msg.id), msg.fromname))
						self.data.deleteMessage(msgid)
					self.data.util.println("All messages deleted")
					self.data.stateChange("mail_purgingend")
			else:
				self.data.stateChange("mail_offerpurgedeclined")
		self.data.stateChange("mail_offerpurgeend")

	def deleteMessage(self,msgid):
		msg = self.data.getMessage(msgid)
		self.data.stateChange("mail_deleteconfirmstart")
		confirm = self.data.util.yesnoprompt("Delete message '%s' from %s? " % (msg.subject,msg.fromname))
		self.data.stateChange("mail_deleteconfirmend")
		if confirm:
			self.data.stateChange("mail_deletingstart")
			self.data.deleteMessage(msgid)
			self.data.stateChange("mail_deletingend")
	
		
	def sendMail(self,toname = None,subject = None,text = None):
		
		destination = toname
		if destination == None:
			self.data.stateChange("mail_sendtopromptstart")
			destination = self.data.util.prompt("Send MAIL to: ")
			self.data.stateChange("mail_sendtopromptend")
			if destination.strip() == "":
				self.data.stateChange("mail_cancelnotostart")
				self.data.util.println("Message cancelled")
				self.data.stateChange("mail_cancelnotoend")
				return
		
		if subject == None:
			self.data.stateChange("mail_sendsubjectpromptstart")	
			subject = self.data.util.prompt("\nSubject: ")
			self.data.stateChange("mail_sendsubjectpromptend")
			if subject.strip() == "":
				self.data.stateChange("mail_cancelnosubjectstart")
				self.data.util.println("Message cancelled")
				self.data.stateChange("mail_cancelnosubjectend")
				return
		
		self.data.stateChange("mail_sendeditstart")	
		editor = Editor()
		if text == None:
			text = ""
		else:
			print "TEXT=" + str(text)
		theText = editor.getText(text=text)
		self.data.stateChange("mail_sendeditend")
		
		sentId = self.data.createMessage(self.currentUser.username,destination.strip(),subject.strip(),theText)
		if sentId == None:
			self.data.stateChange("mail_notsentstart")
			self.data.util.println("Message not sent - invalid recipient")
			self.data.stateChange("mail_notsentend")
		else:
			self.data.stateChange("mail_sentstart")
			self.data.util.println("Letter saved.")
			self.data.stateChange("mail_sentend")
	
	
	
	def listMessages(self,messageIds):
		self.data.stateChange("mail_liststart")
		self.data.util.println(" ")
		i = 1
		for msgId in messageIds:
			msg = self.data.getMessage(msgId)
			newFlag = "N "
			if msg.readbyrecipient:
				newFlag = "  "
			self.data.util.println(newFlag + str(i) + " - {0:15} ".format(str(msg.fromname)) + "{0:30}".format(str(msg.subject)) + self.data.util.formatTimeString(msg.sentdate) + " " + self.data.util.formatDateString(msg.sentdate)) 
			i = i + 1			
		self.data.stateChange("mail_listend")
	
			
			
	def displayMessage(self,msgid):
		instance = self.data.getMessage(msgid) 
		self.data.setMessageRead(msgid)
		self.data.util.cls()
		self.data.util.printraw("MsgID: " + str(instance.id) + " received at " + self.data.util.formatDateString(instance.sentdate) + " " + self.data.util.formatTimeString(instance.sentdate))
		self.data.util.printraw("\nFrom: " + instance.fromname.strip())
		self.data.util.printraw("To: " + instance.toname.strip())
		self.data.util.printraw("Subj: " + instance.subject + "\n")
		for msgtext in self.data.getMessagetexts(msgid):
			for line in msgtext.split("\n"):		## We do this so the pager can keep up
				self.data.util.printraw(line)

	def replyOrForward(self, msgid, isReply):		## set to false if forward
		msg = self.data.getMessage(msgid)
		dest = None
		if isReply:
			dest = msg.fromname
		subject = msg.subject
		subjectPrefix = "Fwd: "
		if isReply:
			subjectPrefix = "Re: "
		if not subject.startswith(subjectPrefix):
			subject = subjectPrefix + subject
		msgtext = "\n\n%s wrote on %s: \n" % (msg.fromname, self.data.util.formatDateTimeString(msg.sentdate))
		msgtexts = self.data.getMessagetexts(msgid)
		msgtextlines = []
		for mt in msgtexts:
			for l in mt.split("\n"):
				msgtextlines.append(l)
		for s in msgtextlines:
			msgtext = msgtext + "> " + s + "\n"
		self.sendMail(toname = dest,subject = subject, text=msgtext)

			
	def go(self, command, args):
		self.data.stateChange("mail_start")				
		messageIds = self.data.getMessagesByUser(self.currentUser.username,checkSrm=True)
		if not messageIds == []:
			self.data.stateChange("mail_foundmessages")			
			self.listMessages(messageIds)
			currentMessage = 0
			userQuits = False
			while not userQuits:
				self.data.stateChange("mail_loopstart")
				choice = ""
				if currentMessage > (len(messageIds) - 1):
					## last message
					self.data.stateChange("mail_endpromptstart")
					choice = self.data.util.prompt("[^RET^] End      Mail> ")
					self.data.stateChange("mail_endpromptend")
					choice = choice.strip()
										
					if choice == "a" or choice == "b":  		## show message again or go back
						self.data.stateChange("mail_again")
						currentMessage = currentMessage - 1
						if currentMessage < 0:
							currentMessage = 0	
						self.data.stateChange("mail_displaystart")
						self.data.util.printn("\n^%s^ of ^%s^  " % (str(currentMessage+1), str(len(messageIds))))
						self.displayMessage(messageIds[currentMessage])
						if not choice == "b":
							currentMessage = currentMessage + 1
						self.data.stateChange("mail_displayend")
							
					if choice == "" or choice == "n":
						break

				else:
					self.data.stateChange("mail_nextpromptstart")
					choice = self.data.util.prompt("\n[^RET^] Next     Mail> ")		
					self.data.stateChange("mail_nextpromptend")
					choice = choice.strip()

					if choice == "a" or choice == "b":
						## User chose to redisplay this message, move pointer back by one, but always > 0
						self.data.stateChange("mail_again")
						currentMessage = currentMessage - 1
						if currentMessage < 0:
							currentMessage = 0	
						## FIXME HACK: move the display next message code
						if not choice == "b":
							choice = "n"

					if choice == "" or choice == "n" or choice == "b":
					##	FIXME put in a method
						self.data.stateChange("mail_displaystart")
						self.data.util.printn("\n^%s^ of ^%s^  " % (str(currentMessage+1), str(len(messageIds))))
						self.displayMessage(messageIds[currentMessage])
						if not choice == "b":
							currentMessage = currentMessage + 1
						self.data.stateChange("mail_displayend")

				if choice == "c":
					self.data.stateChange("mail_clsstart")
					self.data.util.cls()
					self.data.stateChange("mail_clsend")
						
				if choice == "l":
					self.data.stateChange("mail_liststart")
					self.listMessages(messageIds)
					self.data.stateChange("mail_listend")
				if choice == "s":
					self.data.stateChange("mail_sendstart")
					self.sendMail()
					self.data.stateChange("mail_sendend")
				if choice == "r":
					self.data.stateChange("mail_replystart")
					self.replyOrForward(messageIds[currentMessage-1],True)
					self.data.stateChange("mail_replyend")
				if choice == "f":
					self.data.stateChange("mail_forwardstart")
					self.replyOrForward(messageIds[currentMessage-1],False)
					self.data.stateChange("mail_forwardend")

				if choice == "d":
					self.data.stateChange("mail_deletestart")
					self.deleteMessage(messageIds[currentMessage-1])
					self.data.stateChange("mail_deleteend")
					messageIds = self.data.getMessagesByUser(self.currentUser.username)
					if messageIds == []:
						break
					else:
						currentMessage = 0
				if choice == "q":
					userQuits = True
				if choice.isdigit():
					## Messages are numbered from 1 to len on screen, but stored 0 to len-1
					self.data.stateChange("mail_jumpstart")
					chosenMessage = int(choice)
					if chosenMessage > 0 and chosenMessage <= len(messageIds):
						self.data.stateChange("mail_jumpgoodstart")
						currentMessage = chosenMessage - 1
						self.displayMessage(messageIds[currentMessage])
						currentMessage = currentMessage + 1
						self.data.stateChange("mail_jumpgoodend")
					else:
						self.data.stateChange("mail_jumpbadstart")
						self.data.util.println("\nMessage out of range.\n")
						self.data.stateChange("mail_jumpbadend")
				self.data.stateChange("mail_loopend")
			self.data.stateChange("mail_prepurge")
			self.offerPurge(messageIds)
			self.data.stateChange("mail_postpurge")
		else:
			self.data.stateChange("mail_nomailstart")
			self.data.util.println("No mail.")
			self.data.stateChange("mail_nomailsendstart")
			self.sendMail()	
			self.data.stateChange("mail_nomailsendend")
			self.data.stateChange("mail_nomailend")
		self.data.stateChange("mail_end")
		return		
		
		