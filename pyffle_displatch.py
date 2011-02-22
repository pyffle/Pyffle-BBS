## Models for SqlAlchemy version 6
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref
from sqlalchemy import *
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.orm import sessionmaker
from pyffle_tables import *
from pyffle_data import *
import pyffle_mail
from datetime import datetime
import sys
import getpass
import os
import re

class PyffleUtil:
	data = None
	currentUser = None
	bold = False
	lastInput = ""
	
	texts = {}
	
	def helpMenu(self,words,header="\nInformation Available:",maxCols = 4,prompt = "\n\nHelp> ",listwords=True):
		userQuits = False
		while not userQuits:
			self.cls()
			self.println(header)
			self.println("")
			col = 0
			if listwords:
				for word in words:
					if not word.startswith("."):
						self.printn(word.upper() + "    ")
						col = col + 1
						if col > maxCols:
							self.println("")
							col = 0
			choice = self.prompt(prompt)
			choice = choice.lower()
			if choice in words.keys():
				self.println("")
				self.printPaged(words[choice])
				self.prompt("\nPress ENTER..")
			if choice == "q":
				userQuits = True
			if choice == "?":
				self.data.util.println("Select a topic from above or Q to quit..")				
				self.prompt("\nPress ENTER..")
				validChoice = True
			
	def loadWords(self,path):
		words =  os.listdir(path)
		
		self.debugln("Loading words: " + str(words))
		rv = {}
		for word in words:
			if not word.startswith("."):
				f = open(path + "/" + word) ## FIXME portable path separator
				wordContent = f.read()
				word = word.lower()
				rv[word] = wordContent
				f.close()
		return rv
	def toggleBold(self):
		rv = ""
		if self.bold:
			## Turn bold off
			rv = "\x1b[0m"
			self.bold = False
		else:
			rv = "\x1b[7m"
			self.bold = True
		return rv
		
	curRow = 0
	def resetPager(self):
		self.curRow = 0
	
	def addToPager(self,i):
		self.curRow = 		self.curRow + i

	def checkPager(self):
		if not self.currentUser == None:
			if self.curRow >= self.currentUser.pagelength - 1:
				self.prompt("^More^")
				self.resetPager()

		
	def cls(self):
		os.system("clear")
		self.resetPager()
	
	def readline(self):
		return sys.stdin.readline()
		

	def formatTimeString(self,date):
		return str(date.strftime("%H:%M"))

	def formatDateString(self,date):
		return str(date.strftime("%Y-%m-%d"))

	def formatDateTimeString(self,date):
		return str(date.strftime("%Y-%m-%d %H:%M"))
	def getCurrentTimeString(self):
		return self.formatTimeString(datetime.now())

	def getCurrentDateString(self):
		return self.formatDateString(datetime.now())


	def yesnoprompt(self,s,bold=True):
		if bold:
			s = s + "^Y^/^N^ "
		choice = self.prompt(s)
		choice = choice.lower()
		if choice == 'y' or choice == 'yes':
			return True
		return False
		
		
	def readPassword(self,prompt=""):
		return getpass.getpass(prompt)	
		
	def promptDefault(self,s,default):
		choice = self.prompt(s + " [%s] " % (default))
		if choice == "":
			choice = default
		return choice

	def prompt(self,s):
		self.resetPager()
		self.debugn("ROW=" + str(self.curRow) + "|")
		self.printn(s)
		choice = self.readline()
		self.addToPager(1)
		return choice.strip()

	def doBolds(self,s):
		rv = ""
		wasPercent = False
		for c in s:
			if c == "%":
				wasPercent = True
			else:
				if c == "^":
					if wasPercent:
						rv = rv + "^"
					else:
						rv = rv + self.toggleBold()
					wasPercent = False
				else:
					rv = rv + c
					wasPercent = False
		return rv
	
	def expandText(self,text):
		newText = re.sub(r'%$',r'',text);
		newText = newText.replace("%|","\n")
		if not self.currentUser == None:
			newText = newText.replace("%c",str(self.currentUser.timescalled));
			newText = newText.replace("%!",str(self.data.getSystemCalls()));
			newText = newText.replace("%@",str(self.currentUser.datefastlogin));
			newText = newText.replace("%A",self.currentUser.username);
			newText = newText.replace("%F",self.currentUser.realname)
			newText = newText.replace("%G","<n/a>")
			newText = newText.replace("%L",self.currentUser.fakelevel)
			newText = newText.replace("%M","14")	## FIXME WTF is this? 'Moves'? 
			newText = newText.replace("%N",self.data.getCurrentBoard())	
			newText = newText.replace("%O",self.data.getTimeLeft())
			newText = newText.replace("%P",str(self.currentUser.accesslevel))
			newText = newText.replace("%R",self.currentUser.comment)
			newText = newText.replace("%S","<n/a>")
			newText = newText.replace("%U","<n/a>")
			newText = newText.replace("%W",self.currentUser.fullidentity)			
			newText = newText.replace("%Z","<n/a>")		## FIXME add Zippy cookies
			newText = newText.replace("%a",str(self.data.currentUser.accesslevel))
			newText = newText.replace("%b","LOCAL")		## FIXME 
			newText = newText.replace("%c",str(self.currentUser.timescalled));
			newText = newText.replace("%d","<n/a>");## FIXME, get the TTY somehow
			newText = newText.replace("%e",self.currentUser.externaleditor);## FIXME, get the TTY somehow
			newText = newText.replace("%f","<n/a>");## FIXME, get the TTY somehow
			newText = newText.replace("%m",str(len(self.data.getNewMessages())))
			newText = newText.replace("%p",str(self.currentUser.messagesposted))
			newText = newText.replace("%r",str(self.currentUser.kbdownloaded))
			newText = newText.replace("%s",str(self.currentUser.kbuploaded))
			newText = newText.replace("%t",str(self.currentUser.terminal))
			newText = newText.replace("%v","<n/a>")
			newText = newText.replace("%t",str(self.currentUser.transferprotocol))
			newText = newText.replace("%#","<n/a>")
			newText = newText.replace("%?","<n/a>")

		if not self.data == None:
			newText = newText.replace("%l",self.data.getLastUser()[0])
			newText = newText.replace("%n",self.data.getNodename())
			newText = newText.replace("%o",self.data.static.options["organ"])
			newText = newText.replace("%u",self.data.static.options["uucpname"])
			newText = newText.replace("%&",self.data.getPyffleVersionString())
			newText = newText.replace("%V",self.data.getPyffleVersionShortString())
			newText = newText.replace("%B",self.data.getCurrentBoardString())
			newText = newText.replace("%$",str(self.data.getTotalMessageCount()))


		newText = newText.replace("%T",self.getCurrentTimeString())
		newText = newText.replace("%D",self.getCurrentDateString())
		newText = newText.replace("%i",self.lastInput)
		newText = newText.replace("~*","\x1b[2J") 
		newText = newText.replace("~","") 
		newText = newText.replace("%%","%")
		newText = self.doBolds(newText)
		return newText
		
	DEBUG = False
	
				
	def debugln(self,s):
		self.debugn(s + "\n")

	def debugn(self, s):
		if self.DEBUG:
			self.printrawn("### " + s)
		
	def println(self,s):		
		self.printn(self.expandText(s)+"\n")
	
	def printraw(self,s):
		self.printrawn(s+"\n")

	def printrawn(self,s):
		self.addToPager(s.count("\n"))
		sys.stdout.write(s)
		self.checkPager()
		
	def printn(self,s):
		s = self.expandText(s)		
		self.addToPager(s.count("\n"))
		sys.stdout.write(s)
		self.checkPager()
	
	def printPaged(self,s):
		for line in s.split("\n"):
			self.println(line)	

	def printPagedRaw(self,s):
		for line in s.split("\n"):
			self.printraw(line)	
				
###    %	Description          Example

###    %A	account              "john"
###    %B	name of board        "[#1: the Meeting Place]"
###    %C	print a cookie       <prints a cookie>
###    %D	date                 "27-Jul-92"
###    %F	first name           "Francesco"
###    %G	group(s)             "42"
###    %L	fake level           "NiNE"
###    %M	moves                "14"
###    %N	message base         "1"
###    %O	time left online     "58"
###    %P	privilege            "0"
###    %R	rank or remark       "100 billion bottles"
###    %S    time spent online    "2"
###    %T	time                 "6:29p"
###    %U	user index in pw     "61"
###    %V    version              "1.65"
###    %W	who (identity)       "Jose Jimenez"
###    %Z	print Zippy cookie   <prints a cookie>

###    %a	access level         "6"
###    %b	modem speed "baud"   "2400", or "LOCAL"
###    %c	user calls           "56"
###    %d	device number        "1"
###    %e	editor		     "vi"
###    %f    file directory       "/files"
###    %i	input line           "something someone typed"
###    %l	last caller          "Dan Quayle"
###    %m	new local messages   "31"
###    %n	node name            "unknown.UUCP"
###    %o	organization         "Kentucky Fried BBS +1 408 245 SPAM"
###    %p	user posts           "5"
###    %r	k received (UL'd)    "315"
###    %s	k sent (DL'd)        "1771"
###    %t	terminal type        "vt100"
###    %u	UUCP name            "vegas"
###    %v	voting number        "91"
###    %x	transfer protocol    "X"

###    %!	system calls         "51455"
###    %$	system posts	     "14201"
###    %#	user's telephone     "408/767-1506"
###    %@	last call date       "22-Jul-89  5:08"
###    %?	[chat] attempted     "[chat]"

###    %[	lowest message       "1401"
###    %=	current message      "1457"
###    %+	next message         "1458"
###    %]	highest message      "1460"

###    %|	carriage return      <carriage return>
###    %^	caret                "^"
###    %%	percent sign         "%"

###  ^	toggle inverse on/off, ONLY if vt100 mode (DOS) or
### 	the terminal supports emphasized printing (Unix termcap).

###    %j	is used only if you have the voting booth, and will
###     	display a message if there is a new topic.
		