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
from pyffle_exception import *
from pyffle_editor import Editor
from datetime import datetime
import sys
import getpass
import os
import tempfile

def getIdentity():
	return "pyffle_boards v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None

	def eventDispatched(self, event):
		pass
		


	def resetScan(self):
		self.data.stateChange("board_resetstart")		
		self.currentUser.datelastnewscan = None
		self.data.storeUser(self.currentUser)
		self.currentUser.datelastnewscan = datetime.fromtimestamp(0)
		self.data.storeUser(self.currentUser)
		self.data.util.println("Scan has been reset to epoch")
		self.data.stateChange("board_resetend")		
		
		
	## UI for displaying a board list		
	def listBoards(self, boards):
		## Loop through board objects, display one numbered line / board
		self.data.stateChange("board_listboardsstart")
		self.data.util.println("\nBoards available:")	
		i = 1
		for board in boards:
			if not board.name.startswith('__'):
				if self.data.srmcheck(board.aclid,self.currentUser.username,"READ",minlevel=board.minreadlevel):
					self.data.util.println(" [^" + str(i) + "^] " + str(board.name) + " - (" + board.description + ") ") 
			i = i + 1
		self.data.stateChange("board_listboardsend")


	## UI for selecting a message board
	def select(self):
		self.data.stateChange("board_selectstart")
		## Load board objects, pass them to listBoards() to display
		boards = self.data.getBoards()
		self.listBoards(boards)
		## Prompt user for board
		self.data.stateChange("board_selectpromptstart")
		choice = self.data.util.prompt("\nSelect board: ")	
		self.data.stateChange("board_selectpromptend")
		self.data.setCurrentBoard(boards[int(choice)-1].name)

	
	## UI for displaying a message list
	def listPosts(self,messageIds):
		## Loop through the message ids, load message object, display one numbered line / message
		self.data.util.println(" ")
		i = 1
		try:
			for msgId in messageIds:
				msg = self.data.getMessage(msgId)
				self.data.util.println("{0:5}".format(str(i)) + " {0:15} ".format(str(msg.fromname)[0:14]) + "{0:30}".format(str(msg.subject)[0:29]) + self.data.util.formatTimeString(msg.sentdate) + " " + self.data.util.formatDateString(msg.sentdate)) 
				i = i + 1
		except PyffleException as ex:
			pass	## Catch a user break
	## UI for displaying a message in boardname, current = current message being red, high = highest in board
	def displayMessage(self,msgid,boardname,current,high):
		self.data.stateChange("board_displaystart")
		## Load the message object from the DB
		instance = self.data.getMessage(msgid) 

		## Clear the user's screen
		self.data.util.cls()

		self.data.stateChange("board_displayhdrstart")
		## Top line: Msgin and boardname, followed by current/high, in reverse video
		self.data.util.printn("^{0:<39}".format("#%s in %s" % (str(instance.id),boardname)))
		self.data.util.println("{0:>39}^".format("(%s/%s)" % (str(current+1), str(high))))	## we're now back to (back to normal video)
		## Header..
		self.data.util.printraw("From: " + instance.fromname.strip())
		if not instance.toname == None:
			self.data.util.printraw("To: " + instance.toname.strip())
		self.data.util.printraw("Subj: " + instance.subject)
		## Bottom line: Date and time in reverse video
		self.data.util.println("^{0:>78}^".format("%s %s" % (self.data.util.formatDateString(instance.sentdate),self.data.util.formatTimeString(instance.sentdate))))
		self.data.stateChange("board_displayhdrend")
		
		self.data.stateChange("board_displaybodystart")		
		## Finally the message itself
		try:
			for msgtext in self.data.getMessagetexts(msgid):
				for line in msgtext.split("\n"):
					self.data.util.printraw(line)
		except PyffleException as ex:
			pass	## Catch a user break
		self.data.stateChange("board_displaybodyend")
		self.data.stateChange("board_displayend")


			
	def read(self,messageIds=None):
		self.data.stateChange("board_readstart")
		## If we get passed some ids, we are being called from a new scan
		inScan = False
		if messageIds == None:
			self.data.stateChange("board_readnormal")
			messageIds = self.data.getMessagesByBoardname(self.data.getCurrentBoard())
		else:
			self.data.stateChange("board_readinscan")
			inScan = True
		
		## We will return this to tell any scan if the user wanted to abort or not
		userAbort = False
		
		## If there are messages, loop through them, starting with a list
		if not messageIds == []:
			self.data.stateChange("board_liststart")
			self.listPosts(messageIds)
			self.data.stateChange("board_listend")
			currentMessage = 0
			userQuits = False
			self.data.stateChange("board_readpostloop")
			while not (userQuits):
				choice = ""
				
				## Check if we're at the end of the messages
				if currentMessage > (len(messageIds) - 1):
					## We are at the end of the messages, display relevant prompt				
					if inScan:
						self.data.stateChange("board_readinscanendpromptstart")
						choice = self.data.util.prompt("^P^ost, ^L^ist, [1-" +str(len(messageIds)) + "] ^Q^uit, ^!^ Abort Scan: ")		
						self.data.stateChange("board_readinscanendpromptend")
					else:
						self.data.stateChange("board_readnormalendpromptstart")
						choice = self.data.util.prompt("^P^ost, ^L^ist, [1-" +str(len(messageIds)) + "] ^Q^uit: ")		
						self.data.stateChange("board_readnormalendpromptend")
				else:
					## We are not at the end of the messages, display relevant prompt
					if inScan:
						self.data.stateChange("board_readinscanpromptstart")
						choice = self.data.util.prompt("\n[^RET^] 1-" +str(len(messageIds)) + ", ^P^ost, ^L^ist, ^Q^uit, ^!^ Abort Scan: ")
						self.data.stateChange("board_readinscanpromptend")
					else:
						self.data.stateChange("board_readnormalpromptstart")
						choice = self.data.util.prompt("\n[^RET^] 1-" +str(len(messageIds)) + ", ^P^ost, ^L^ist, ^Q^uit: ")
						self.data.stateChange("board_readnormalpromptend")
						
				## Clean the choice string, see what the user wants to do
				choice = choice.strip()

				if choice == "":
					## User pressed enter, try to show the next message
					if not currentMessage > (len(messageIds) - 1):
						self.displayMessage(messageIds[currentMessage],self.data.getCurrentBoard(),currentMessage,len(messageIds))
						currentMessage = currentMessage + 1
						self.data.stateChange("board_readnextmessage")
					else:
						## At the end of the messages, tell the user
						self.data.stateChange("board_readendofmsgsstart")
						self.data.util.println("- End of messages -")
						self.data.stateChange("board_readendofmsgsend")

				if choice == "f":
					self.data.stateChange("board_readfollowupstart")
					msgid = messageIds[currentMessage-1]
					msg = self.data.getMessage(msgid)
					subject = msg.subject
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
					self.data.stateChange("board_followupcreatestart")	
					self.post(subject=subject,theText=msgtext)
					self.data.stateChange("board_followupcreateend")
					self.data.stateChange("board_readfollowupend")

				if choice == "!" and inScan:
					## If the user is in a new scan and hits !, we stop and let the scan know
					self.data.stateChange("board_readuserabort")
					userAbort = True
					break
					
				if choice == "p":
					## User wants to post a message, let's do it
					self.data.stateChange("board_readpoststart")
					self.post()
					self.data.stateChange("board_readpostend")

				if choice == "l":
					self.data.stateChange("board_readliststart")
					## User wants to see the message list again
					self.listPosts(messageIds)
					## Not sure whether to reset the list?
					## currentMessage = 0
					self.data.stateChange("board_readlistend")

				if choice == "q":
   					self.data.stateChange("board_readuserquit")
					## User wants to stop 
					userQuits = True
					break
					
				if choice.isdigit():
					## The user is trying to jump to a numbered message
					## Messages are numbered from 1 to len on screen, but stored 0 to len-1
					self.data.stateChange("board_readjumpstart")
					chosenMessage = int(choice)
					if chosenMessage > 0 and chosenMessage <= len(messageIds):
						## It's a valid choice, set the pointer, show the message
						currentMessage = chosenMessage - 1
						self.displayMessage(messageIds[currentMessage],self.data.getCurrentBoard(),currentMessage,len(messageIds))
						self.data.stateChange("board_readjumpok")
						## Move to the next message 
						currentMessage = currentMessage + 1
					else:
						self.data.stateChange("board_readjumpbad")
						## The user tried to choose an invalid message
						self.data.util.println("\nMessage out of range.\n")
					self.data.stateChange("board_readjumpend")
			self.data.stateChange("board_readpostloopend")
			## If the user hit !, we'll return True to a scan	
			return userAbort		
		else:
			## No messages in this area.
			self.data.stateChange("board_reademptystart")
			self.data.util.println("No posts.")
			self.data.stateChange("board_reademptyend")


	def new(self):
		## FIXME - args
		## FIXME - join
		
		## Remember the currently selected board 
		oldCurrent = self.data.getCurrentBoard()
		
		## Get a list of all boards FIXME: Should only get the subscribed ones
		boards = self.data.getBoards()
		self.data.stateChange("board_newstart")	

		if self.currentUser.datelastnewscan == None:
			self.data.stateChange("board_newnodatestart")	
			self.data.util.println("No last scan, setting to epoch..")
			self.resetScan()
			self.data.stateChange("board_newnodateend")

		## Loop through the boards
		
		self.data.util.println("\nScanning for new messages..\n")
		self.data.stateChange("board_newloop")
		scannedBoards = 0
		for board in boards:
			if not board.name.startswith('__') and  (board.id in self.data.getJoinedBoardids()):   ## ignore any internal boards
				## Check that we're allowed to read this board
				if self.data.srmcheck(board.aclid,self.currentUser.username,"READ",minlevel=board.minreadlevel):
					## Get the messages
					scannedBoards = scannedBoards + 1 
					msgids = self.data.getMessagesSince(board,self.currentUser.datelastnewscan) 
					if not msgids == []:
						self.data.stateChange("board_newfoundstart")
						self.data.util.println("  {0:30}".format(board.name) + " " + str(len(msgids)) + " new message(s)")
						self.data.stateChange("board_newfoundend")
					else:
						self.data.stateChange("board_newemptystart")
						self.data.util.println("  {0:30}".format(board.name) + " No new messages")
						self.data.stateChange("board_newemptyend")
		self.data.stateChange("board_newloopend")
		if scannedBoards == 0:
			self.data.stateChange("board_newjoinwarnstart")
			self.data.util.println("No boards actually scanned, check your JOIN settings..")
			self.data.stateChange("board_newjoinwarnend")
		else:
			self.data.stateChange("board_newsummarystart")
			self.data.util.println("\nScanned %s boards\n" % (str(scannedBoards)))
			self.data.stateChange("board_newsummaryend")
		
		self.data.stateChange("board_newend")
		return

	def scan(self):
		## FIXME - scan dates
		## FIXME - args
		## FIXME - join
		
		## Remember the currently selected board 
		oldCurrent = self.data.getCurrentBoard()
		
		## Get a list of all boards FIXME: Should only get the subscribed ones
		boards = self.data.getBoards()
		## Tell the user what's happening 
		self.data.stateChange("board_scanstartmsgstart")
		self.data.util.prompt("Starting NEW SCAN (you can abort the scan by entering ! at a prompt)\nPress ENTER to start..")
		self.data.stateChange("board_scanstartmsgend")

		if self.currentUser.datelastnewscan == None:
			self.data.stateChange("board_scannodatestart")
			self.data.util.println("No last scan, setting to epoch..")
			self.resetScan()
			self.data.stateChange("board_scannodateend")
		## Loop through the boards
		self.data.stateChange("board_scanloop")		
		scannedBoards = 0
		for board in boards:
			if not board.name.startswith('__')  and  (board.id in self.data.getJoinedBoardids()):   ## ignore any internal boards
				## Check that we're allowed to read this board
				if self.data.srmcheck(board.aclid,self.currentUser.username,"READ",minlevel=board.minreadlevel):
					scannedBoards = scannedBoards + 1
					## Get the messages
					msgids = self.data.getMessagesSince(board,self.currentUser.datelastnewscan) 
					if not msgids == []:
						self.data.stateChange("board_scanfoundnewstart")	
						## If there are any messages, temporarily set the current board to the board we're looking at
						self.data.setCurrentBoard(board.name)
						## Clear the screen
						self.data.util.cls()
						## Scan header
						self.data.util.println("\n^" + board.name + "^     " + str(len(msgids)) + " message(s)")
						## Read the messages we found
						userAbort = self.read(messageIds = msgids)										
						## If the user hit ! during the read, we bail
						self.data.stateChange("board_scanfoundnewend")	

						if userAbort:
							self.data.stateChange("board_scanuserabort")						 
							break
					else:
						self.data.stateChange("board_scanemptyboard")
						self.data.util.println("\nBoard %s has no new messages" % (board.name))
		self.data.stateChange("board_scanloopend")
							
		if scannedBoards == 0:
			self.data.stateChange("board_scanjoinwarnstart")
			self.data.util.println("No boards actually scanned, check your JOIN settings..")
			self.data.stateChange("board_scanjoinwarnsend")
		else:
			self.data.stateChange("board_scansummarystart")
			self.data.util.println("\nScanned %s boards" % (str(scannedBoards)))
			self.data.stateChange("board_scansummaryend")
			
			
		## Restore the original selected board to the session				
		self.data.setCurrentBoard(oldCurrent)	
		
		## Set the scan pointer to now
		self.currentUser.datelastnewscan = None
		self.data.storeUser(self.currentUser)
		self.currentUser.datelastnewscan = datetime.now()
		self.data.storeUser(self.currentUser)

		return		
			
		
	def post(self,subject=None,theText=None):
		## Get the board object for the currently selected board	
		board = self.data.getBoardByName(self.data.getCurrentBoard())
		
		## Check that we're allowed to post on it
		if self.data.srmcheck(board.aclid,self.currentUser.username,"POST",minlevel=board.minpostlevel):
			## Get the subject of the post from the user
			if subject == None:
				subject = self.data.util.prompt("\nSubject: ")
			## Launch an editor for the user and get the message text
			if theText == None:
				theText = ""
			editor = Editor()
			theText = editor.getText(text=theText)
			## Confirm the user wants to go through with the posting
			confirm = self.data.util.yesnoprompt("Proceed? ")
			if confirm:
				## They do, create the message
				sentId = self.data.createMessage(self.currentUser.username,None,subject.strip(),theText,board=self.data.getCurrentBoard())
				## Let the user know it was succesful
				self.data.util.println("Message posted.")
				## Update the user's posting stats
				self.data.updateUserPosts()

				## Display a cookie (it's what the old Waffle used to)
				cookieModule = __import__("pyffle_cookie")
				cookieInstance = cookieModule.PyffleModule()
				cookieInstance.data = self.data
				cookieInstance.currentUser = self.currentUser
				cookieInstance.go("justacookie",["justacookie"])
		else:
			## Secure failure
			self.data.util.println("Sorry, you are not allowed post on this board.")

		
	
	def go(self, command, args):
		command = command.strip()
		if command == "reset":
			self.data.stateChange("board_cmdresetstart")
			self.resetScan()
			self.data.stateChange("board_cmdresetend")			
		if command == "select":
			self.data.stateChange("board_cmdselectstart")
			self.select()
			self.data.stateChange("board_cmdselectend")			
		if command == "post":
			self.data.stateChange("board_cmdpoststart")
			self.post()
			self.data.stateChange("board_cmdpostend")
		if command == "read" or command == "list":
			self.data.stateChange("board_cmdreadstart")
			self.read()			
			self.data.stateChange("board_cmdreadend")
		if command == "new":
			self.data.stateChange("board_cmdnewstart")
			self.new()			
			self.data.stateChange("board_cmdnewend")
		if command == "scan":
			self.data.stateChange("board_cmdscanstart")
			self.scan()			
			self.data.stateChange("board_cmdscanend")
		