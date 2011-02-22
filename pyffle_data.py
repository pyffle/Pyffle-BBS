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
from datetime import datetime
from pyffle_dispatch import PyffleDispatch
import os
import psutil
from threading import Lock
### This is the central class for Pyffle - it deals with:
### 
###  - Message creation/updating/deleting/querying
###  - Logging
###  - Security / ACL/ACE ops
###  - Various housekeeping tasks
###
###  Almost everything in the system has a pointer to an
###  instance of this class and it is the central "switchboard"
###  of the system.
###  
###  Additionally there are calls to and from the Utility class
###  which provides string formatting and I/O etc, that are typically
###  accessed through the data.util. handle.
###  
###  On start up, Pyffle (and stand alone tools), create an instance
###  of PyffleData once a DB session has been set up, and connect it with
###  an instance of PyffleUtility
###  
###  PS: I know this should be refactored :)
###  
###  sampsa

class PyffleData:
	currentUser = None			## The currently logged in user, set by PyffleMain typically
	currentBoard = None			## The currently selected message board

	session = None				## Database sesson
	util = None					## Instance of PyffleUtility, set by PyffleMain typically
	static = None				## Loaded configuration from STATIC file, dictionary

	toolMode = False			## This is set to true when running as a standalone tool to bypass the SRM

	mtaModules = {}				## Modules for MTAs that handle external mail
	mtas = []					## mta entry = [mta module name to be loaded, mta name, mta description]

	loggedIn = False
	sessionRef = None			## id into currentlyon table
	
	staticCookies = None
	
	sessionLock = None
	sessionLocked = False
	def __init__ (self):
		## self.sessionLock = Lock()
		pass
	
	
	def getStaticCookies(self):
		rv = []
		if self.staticCookies == None:
			self.staticCookies = self.util.texts["SYSTEM"]["cookies"].split("|") 
		rv = self.staticCookies
		return rv
	## easiest way to do multithreading - grab a local copy of the DB session...
	def getLocalSession(self):
		Session = sessionmaker()
		
		##		engine = create_engine('postgresql://postgres:f00btron@localhost/pyffledev', echo=False)
		engine = create_engine(self.static.options['pyffle.dburl'], echo = False)
		Session.configure(bind=engine)
		
		localSession = Session()		
		return localSession
		
	def getSession(self):
		return self.session
	
	def lockSession(self):
		##self.sessionLock.acquire()
		##self.sessionLocked = True
		pass 
		
	def releaseSession(self):
		##if self.sessionLocked:
		##	self.sessionLock.release()
		##	self.sessionLocked = False	
		pass
		

	def pluginDeleteSystem(self,key):
		if not self.currentUser == None:
			username = self.currentUser.username
		else:
			username = "<none>"
		self.lockSession()
		for object in self.getSession().query(Pluginsystem).filter(Pluginsystem.key == key):
			self.getSession().delete(object)
			self.getSession().commit()
			self.logEntry(self.LOGINFO,"DELETE/PLUGIN/SYSTEM",str(username),"Deleted |%s|=|%s|" % (str(key),str(object.value)))
		self.releaseSession()
			
	def pluginDeleteUser(self,username,key):
		self.lockSession()
		for object in self.getSession().query(Pluginuser).filter(Pluginuser.key == key).filter(Pluginuser.username == username):
			self.getSession().delete(object)
			self.getSession().commit()
			self.logEntry(self.LOGINFO,"DELETE/PLUGIN/USER",str(username),"Deleted %s's |%s|=|%s|" % (str(username),str(key),str(object.value)))
		self.releaseSession()
			
	def pluginWriteSystem(self,key,value):
		if not self.currentUser == None:
			username = self.currentUser.username
		else:
			username = "<none>"

		self.pluginDeleteSystem(key)
		object = Pluginsystem()
		object.key=key
		object.value=value
		self.lockSession()
		self.getSession().add(object)
		self.getSession().commit()
		self.releaseSession()
		self.logEntry(self.LOGINFO,"CREATE/PLUGIN/SYSTEM",str(username),"Stored |%s|=|%s|" % (str(key),str(value)))
		
	def pluginWriteUser(self,username,key,value):
		self.pluginDeleteUser(username,key)
		object = Pluginuser()
		object.username=username
		object.key=key
		object.value=value
		self.lockSession()
		self.getSession().add(object)
		self.getSession().commit()
		self.releaseSession()
		self.logEntry(self.LOGINFO,"CREATE/PLUGIN/USER",str(username),"Stored %s's |%s|=|%s|" % (str(username),str(key),str(value)))

	def pluginReadSystem(self,key):
		if not self.currentUser == None:
			username = self.currentUser.username
		else:
			username = "<none>"

		rv = None
		self.lockSession()
		for object in self.getSession().query(Pluginsystem).filter(Pluginsystem.key == key):
			rv = object.value
			self.logEntry(self.LOGINFO,"READ/PLUGIN/SYSTEM",str(username),"Read |%s|=|%s|" % (str(key),str(rv)))
			break
		self.releaseSession()

		return rv
		
					
	def pluginReadUser(self,username,key):
		rv = None
		for object in self.getSession().query(Pluginuser).filter(Pluginuser.key == key).filter(Pluginuser.username == username):
			rv = object.value
			self.logEntry(self.LOGINFO,"READ/PLUGIN/USER",str(username),"Read %s's |%s|=|%s|" % (str(username),str(key),str(rv)))
			break
		return rv
		
## Logging functions start

###
### Logging criticality levels
###
	LOGCRIT = 5
	LOGWARN = 4
	LOGNORMAL = 3
	LOGINFO = 2
	LOGDEBUG = 1
	
	LOGLEVEL=3
	## Post an entry to the log
	def logEntry(self,level,code,subject,description):
		if level >= self.LOGLEVEL:
			entry = Logentry()
			entry.level = level
			entry.code = code
			entry.subject = subject
			entry.description = description
			entry.date = datetime.now()
			self.getSession().add(entry)
			self.getSession().commit()
		
	## Returns the name of the previous caller from the system log
	def getLastUser(self):	
		## since our call has already been logged, grab the one before us
		## FIXME - check for None
		lastUsers = self.getLastUsers(2)
		if lastUsers == None or len(lastUsers) < 2:
			return "  "
		else:
			return lastUsers[1]
	
	## Log a loginfailure
	def logLoginFail(self,username):
		self.logEntry(self.LOGWARN,"LOGIN/FAILURE",str(username),"%s failed to log in, bad credentials" % (str(username)))

	def addToCurrentlyon(self):
		entry = Currentlyon()
		entry.activity 	= ""
		entry.origin 		= ""		## FIXME - add origin here
		entry.username 	= self.currentUser.username
		entry.dateon 		= datetime.now()
		entry.pid			= os.getpid()
		self.getSession().add(entry)
		self.getSession().commit()
		self.sessionRef = entry.id
	
	def resetCurrentlyOn(self):
		for entry in	self.getSession().query(Currentlyon):
			self.getSession().delete(entry)
			self.getSession().commit()
			self.sessionRef = None
			

	def removeFromCurrentlyon(self):
		for entry in	self.getSession().query(Currentlyon).filter(Currentlyon.id == self.sessionRef):
			self.getSession().delete(entry)
			self.getSession().commit()
			self.sessionRef = None
		
	def getCurrentlyonEntries(self):
		rv = []
		entries =	self.getSession().query(Currentlyon)
		for entry in entries:
			## check that the entry is still valid (i.e. the process is still running)
			if entry.pid in psutil.get_pid_list():
				## print "%s is still valid" % (entry.pid)
				rv.append(entry)
			else:
				## print "%s is a stale PID, deleting" % (entry.pid)
				## it's not, remove from the table
				self.getSession().delete(entry)
				self.getSession().commit()
		return rv
		
		
	## Log a succesful start to session
	def logCall(self):
		loggedIn = True
		self.addToCurrentlyon()
		if self.currentUser.timescalled == None:
			self.currentUser.timescalled = 0
		self.currentUser.timescalled = int(self.currentUser.timescalled) + 1
		self.getSession().add(self.currentUser)
		self.getSession().commit()
		self.logEntry(self.LOGNORMAL,"LOGIN/SUCCESS",self.currentUser.username,"%s logged in normally" % (self.currentUser.username))

	## Log a succesful logout
	def logLogout(self):
		self.removeFromCurrentlyon()
		loggedIn = False
		self.currentUser.datefastlogin = datetime.now()
		if self.currentUser.datefirstlogin == None:
			self.currentUser.datefirstlogin = self.currentUser.datefastlogin
		self.getSession().add(self.currentUser)
		self.getSession().commit()
		self.logEntry(self.LOGNORMAL,"LOGOUT/SUCCESS",self.currentUser.username,"%s logged out normally" % (self.currentUser.username))
	
	## Return a list of num x log entries, each entry being a list:
	## [entry.level,entry.code,entry.subject,entry.date,entry.description]
	def getLog(self,num = 22, level = -1):
		rv = []
		i = 0
		for entry in self.getSession().query(Logentry).filter(Logentry.level >= level).order_by(Logentry.date.desc()):
			rv.append([entry.level,entry.code,entry.subject,entry.date,entry.description])
			i = i + 1
			if i == num:
				break
		return rv
	
	## Returns the amount of calls to the system from the system log
	def getSystemCalls(self):
		rv = self.getSession().query(Logentry).filter(Logentry.code == "LOGIN/SUCCESS").count()
		return rv
	
	## Returns a list of num last callers, each entry being a list of:
	## [subject == caller username, date]
	def getLastUsers(self,num = 20):
		rv = []
		i = 0
		for entry in self.getSession().query(Logentry).filter(Logentry.code == "LOGIN/SUCCESS").order_by(Logentry.date.desc()):
			rv.append([entry.subject,entry.date])
			i = i + 1
			if i > num:
				break
		return rv
		
	
### MTA functions start	
	
	## Imports the modules for the mtas given	
	def loadMtaList(self,mtas):
		### single mta = [module.py, mta name, mta description]
		self.mtas = mtas
		for mta in mtas:
			self.mtaModules[mta[1]] = (__import__(mta[0]))


	## Loops through out MTAs and tries to parse an external addres
	## to match an internal user. Returns a string if the parsing was succesful,
	## None if not
	def parseIncomingAddress(self,toname):
		toname = toname.strip()
		self.util.debugln("TONAME=" + toname)
		if self.userExists(toname):
			## Got a local user, great, this will be simple
			return toname;
		else:
			## OK, the user is remote - let's see if anybody will accept delivery
			self.util.debugln("Address not local, checking MTAs")
			for mtaName in self.mtaModules.keys():
				## Loop through our MTAs, instantiating each one until
				## we get one that accepts the address
				mta = self.mtaModules[mtaName]
				mtaInstance = mta.PyffleMta()
				mtaInstance.data = self
				mtaInstance.currentUser = self.currentUser
				if mtaInstance.matchIncomingAddress(toname):
					username,system = mtaInstance.parseIncomingAddress(toname)
					## FIXME: check destination system name here too
					if (not username == None) and (not username == ""):
						## Cool, this MTA likes the address, let's jump out of this
						self.util.debugln("MTA " + mtaName + " thinks this is for " + username)
						return username					
			## Address doesn't appear to be valid - bork, return without sending or storing anything
			self.util.debugln("Destination address invalid, no MTA will accept destination")
			return None
			

### Event dispatcher
	dispatcher = None
	def setDispatcher(self,d):
		self.dispatcher = d

	def stateChange(self,s,params=None):
		self.dispatcher.stateChange(s,args=params)

### Housekeeping / misc functions start

	## Returns a string describing the amount of time the user has left.
	## Not implemented.
	def getTimeLeft(self):
		return "59 mins"
		
		
	def getPyffleVersionString(self):
		return "Pyffle v0.01, still in the box."
		
	## Returns a short form of the version string
	def getPyffleVersionShortString(self):
		return "0.01"
		
	## Returns the username of the system operator
	def getSysopId(self):
		return "system"			## FIXME Static?


	def getNodename(self):
		return self.static.options["node"]	

### JOIN functions start...
	def unjoinByBoardid(self, boardid, username = None):
		if username == None:
			username = self.currentUser.username

		for join in self.getSession().query(Joinedboard).filter(Joinedboard.boardid == boardid).filter(Joinedboard.username == username):
			self.getSession().delete(join)
			self.getSession().commit()
		self.logEntry(self.LOGNORMAL,"UNJOIN/BOARD","BOARDID:" + str(boardid),"%s UNJOINed %s " % (username,str(boardid)))

	def joinAll(self,username = None):

		if username == None:
			username = self.currentUser.username
		for boardid in self.getBoardids():
			self.joinByBoardid(boardid,username)

		
	def unjoinAll(self,username = None):

		if username == None:
			username = self.currentUser.username

		for boardid in self.getJoinedBoardids():
			self.unjoinByBoardid(boardid,username)
			
	def joinByBoardid(self, boardid, username = None):

		if username == None:
			username = self.currentUser.username

		if self.isJoinedByBoardid(boardid,username):
			return ## Already joined
		join  = Joinedboard()
		join.username = username
		join.boardid = boardid
		self.getSession().add(join)
		self.getSession().commit()
		
		self.logEntry(self.LOGNORMAL,"JOIN/BOARD","BOARDID:" + str(boardid),"%s JOINed %s " % (username,str(boardid)))

		return join.id
		
	def isJoinedByBoardid(self, boardid, username = None):

		if username == None:
			username = self.currentUser.username

		rv = False;
		for joins in self.getSession().query(Joinedboard).filter(Joinedboard.boardid == boardid).filter(Joinedboard.username == username):
			rv = True
			break
		return rv

	def getJoinedBoardids(self, username = None):

		if username == None:
			username = self.currentUser.username

		rv = []
		for boardid in self.getBoardids():
			if self.isJoinedByBoardid(boardid,username):
				rv.append(boardid)
		return rv
		
		
	def joinBoardToggle(self, boardid, username = None):

		print "Toggling %s" % (str(boardid))
		if username == None:
			username = self.currentUser.username


		if self.isJoinedByBoardid(boardid,username):
			print "It's on, turning off %s" % (str(boardid))		
			self.unjoinByBoardid(boardid,username)
		else:
			print "It's off, turning on %s" % (str(boardid))		
			self.joinByBoardid(boardid,username)
			
### Board functions start
	## Returns a descriptive string of the currently selected board
	def getCurrentBoardString(self):
		boardname = self.getCurrentBoard()
		description = ""
		if not boardname == None:
			board = self.getBoardByName(boardname)
			if not board == None:
				description = str(self.getBoardByName(boardname).description)
			
		return "[" + boardname + ": " + description +"]"

	def getCurrentBoard(self):
		return str(self.currentBoard)
		
	def setCurrentBoard(self,boardname):
		rv = False
		board = self.getBoard(self.getBoardid(boardname))
		if self.srmcheck(board.aclid,self.currentUser.username,"READ",minlevel=board.minreadlevel): 
			self.currentBoard = boardname
			rv = True
		return rv


	def getBoardids(self):
		## 
		rv = []
		for theBoard in self.getBoards():
			rv.append(theBoard.id)
		return rv

	def getBoards(self):
		## 
		rv = []
		for theBoard in self.getSession().query(Board).order_by(Board.id):
			rv.append(theBoard)
		return rv

	def getBoardNames(self):
		rv = []
		boards = self.getBoards()
		for board in boards:
			rv.append(board.name)
		return rv
		
	def getBoardByExternalname(self,name):
		for theBoard in self.getSession().query(Board).filter(Board.externalname == name):
			return theBoard
		return None


	def getBoardByName(self,name):
		## 
		for theBoard in self.getSession().query(Board).filter(Board.name == name):
			return theBoard
		return None
		
		
	def getBoard(self,boardid):
		## 
		for theBoard in self.getSession().query(Board).filter(Board.id == boardid):
			return theBoard
		return None
		
	def deleteBoardByBoardid(self, boardid):
		## Delete messages first
		msgids = self.getMessagesByBoardid(boardid)
		for msgid in msgids:
			self.deleteMessage(msgid)
		
		## Get the board
		board = self.getBoard(boardid)
		if not board == None:
			boardname = board.name
	
			
			## remove ourselves
			self.getSession().delete(board)
			self.getSession().commit()		
	
			## Finally delete the ACL
			## self.deleteAcl(board.aclid)
	
		
			self.logEntry(self.LOGNORMAL,"DELETE/BOARD","BOARDID:" + str(boardid),"Board deleted: %s " % (str(boardname)))
		
	def deleteBoardByBoardname(self,	name):
		return self.deleteBoardByBoardid(self.getBoardid(name))
		
		
	def createBoard(self,	name,
							description,
							owner,
							externalname, 
							minreadlevel,
							minpostlevel,
							minoplevel,
							aclid = None):
		#### creates a board
		myBoard = Board()
		myBoard.name = name
		myBoard.description = description
		myBoard.owner = owner
		myBoard.externalname = externalname
		myBoard.minreadlevel = minreadlevel
		myBoard.minpostlevel = minpostlevel
		myBoard.minoplevel = minoplevel
		if aclid == None:
			myAcl = self.createAcl()
			myAcl.description="BOARD: "+name
			self.getSession().add(myAcl)
			self.getSession().commit()					
			aclid = myAcl.id
		myBoard.aclid = aclid
		self.getSession().add(myBoard)
		self.getSession().commit()
		self.logEntry(self.LOGNORMAL,"CREATE/BOARD","BOARDID:" + str(myBoard.id),"Board created: %s " % (str(myBoard.name)))

		return myBoard.id
	
	
	def getBoardid(self,name):
		for instance in self.getSession().query(Board).filter(Board.name == name): 
			return instance.id
		return None

### User functions start

	def updateUserPosts(self):
		if self.currentUser.messagesposted == None:
			self.currentUser.messagesposted = 0
		self.currentUser.messagesposted = self.currentUser.messagesposted + 1
		
		self.getSession().add(self.currentUser)
		self.getSession().commit()


	def registerUser(self,answers):
		theUser = Users()
		theUser.fullidentity = answers["*IDENTITY"].strip()
		theUser.username = answers["*NAME"].strip()
		theAcl = self.createAcl(description="ACL for user " + theUser.username)
		theUser.aclid = theAcl.id
		theUser.password = answers["*PASSWORD"].strip()
		theUser.realname = answers["*FIRST"].strip()
		theUser.comment  = answers["*ASK BACKGROUND"].strip()
		theUser.timescalled = 0
		theUser.datefirstlogin = datetime.now()
		theUser.datefastlogin = datetime.now()
		theUser.messagesposted = 0
		theUser.accesslevel = 10 ## FIXME grab from static
		theUser.fakelevel = "10"
		theUser.transferprotocol = "K"
		theUser.kbuploaded = 0
		theUser.kbdownloaded = 0
		theUser.datelastnewscan = None
		theUser.externaleditor = "pico"
		theUser.consoleeditor = "pico"
		theUser.terminal = "vt100"
		theUser.pagelength = 23
		theUser.disablepagedmsgs = False
		theUser.minutesontoday = -1
		theUser.splashfile = None

		
		self.storeUser(theUser)
		self.currentUser = theUser
		self.util.currentUser = theUser
		self.logEntry(self.LOGNORMAL,"CREATE/USER",str(theUser.username),"Registered new user %s" % (str(theUser.username)))

		return None


	def storeUser(self,theUser):
		theUser.username = theUser.username.lower()
		self.getSession().add(theUser)
		self.getSession().commit()
		self.logEntry(self.LOGINFO,"STORE/USER",str(theUser.username),"Stored user record %s" % (str(theUser.username)))
		
	
	def setPassword(self,password,user = None):
		if user == None:
			user = self.currentUser
		user.password = password
		self.logEntry(self.LOGNORMAL,"ALTER/USER/PASSWORD",str(user.username),"%s changed password" % (str(user.username)))
		self.storeUser(user)
		
	def getUsers(self):
		## There will always be at least the system user, hopefully
		return self.getSession().query(Users)
		
	def getUser(self,username):
		## 
		rv = None
		for theUser in self.getSession().query(Users).filter(Users.username == username.lower()):
			rv = theUser
		return rv
	
	def userExists(self,name):
		## 
	
		found = False
		for myUser in self.getSession().query(Users).filter(Users.username == name):
			found = True
		return found

	## Deletes a message
	## Security is checked	
	def deleteUser(self,username):
		## 
		## let's get the message first so that we can delete it's components
		user = self.getUser(username)
		if not user == None:		
			## remember the acl id for the step after this
			aclid = user.aclid
			
			## delete the user itself
			self.getSession().delete(user)
			self.getSession().commit()
			
			## finally we delete the ACL
			self.deleteAcl(aclid)
			self.logEntry(self.LOGINFO,"DELETE/USER",str(username),"Deleted user: %s" % (str(username)))
			
			return True



### ACL functions start
	def getAcl(self,aclid):
		## 
		theAcl = self.getSession().query(Acl).filter(Acl.id == aclid)[0]
		return theAcl
		

		
	def deleteAcl(self,aclid):
		## delete any ACEs under this id
		self.deleteAces(aclid)
		
		## delete the ACL
		for theAcl in self.getSession().query(Acl).filter(Acl.id == aclid):
			self.getSession().delete(theAcl)
			self.getSession().commit()
			self.logEntry(self.LOGINFO,"DELETE/ACL","ACLID:" + str(aclid),"Deleted ACL: %s" % (str(aclid)))


	def createAcl(self,description=""):
		acl	= Acl()
		acl.description = description
		self.getSession().add(acl)
		self.getSession().commit()
		self.logEntry(self.LOGINFO,"CREATE/ACL","ACLID:" + str(acl.id),"Created ACL: %s" % (str(acl.id)))
		return acl
	
	def getAces(self,aclid,grantordeny):
		rv = []
		aces =	self.getSession().query(Ace).filter(Ace.aclid==aclid).filter(Ace.grantordeny == grantordeny)

		if not aces == None:
			for myAce in aces:
				rv.append([myAce.permission,myAce.subjectid])
		return rv
	def getAclGrants(self,aclid):
		return self.getAces(aclid,"GRANT")
		
	def getAclDenies(self,aclid):
		return self.getAces(aclid,"DENY")
	
### ACE functions start

	def deleteAces(self,aclid):
		## 
		for ace in self.getSession().query(Ace).filter(Ace.aclid == aclid):
			aceid = ace.id
			self.getSession().delete(ace)
			self.getSession().commit()
			self.logEntry(self.LOGINFO,"DELETE/ACE","ACEID:" + str(aceid),"Deleted ACE: %s" % (str(aceid)))
		


	def dropGrant(self,acl, subject, object):
		if self.isGranted(acl,subject,object):
			for myAce in self.getSession().query(Ace).filter(Ace.aclid==acl.id).filter(Ace.subjectid==subject).filter(Ace.permission == object).filter(Ace.grantordeny == "GRANT"):	
				self.getSession().delete(myAce)
				self.getSession().commit()
			self.logEntry(self.LOGINFO,"ACE/DROPGRANT",str(subject),"Dropped grant %s to %s" % (str(object),str(subject)))


	def dropDeny(self,acl, subject, object):
		if self.isDenied(acl,subject,object):
			for myAce in self.getSession().query(Ace).filter(Ace.aclid==acl.id).filter(Ace.subjectid==subject).filter(Ace.permission == object).filter(Ace.grantordeny == "DENY"):	
				self.getSession().delete(myAce)
				self.getSession().commit()
			self.logEntry(self.LOGINFO,"ACE/DROPDENY",str(subject),"Dropped deny %s to %s" % (str(object),str(subject)))

		
	def grant(self,acl, subject, object):

		## FIXME: add checking of pre-existing ACE
		## 
		if self.isGranted(acl,subject,object):
			return;		## This ACE already exists, we don't need to do anything
		myAce = Ace()
		myAce.aclid = acl.id
		myAce.subjectid = subject
		myAce.permission = object
		myAce.grantordeny = "GRANT"
		self.getSession().add(myAce)
		self.getSession().commit()
		self.logEntry(self.LOGINFO,"ACE/GRANT",str(subject),"Granted %s to %s" % (str(object),str(subject)))



		
	def deny(self,acl, subject, object):
		## 
		if self.isDenied(acl,subject,object):
			return;		## This ACE already exists, we don't need to do anything
		myAce = Ace()
		myAce.aclid = acl.id
		myAce.subjectid = subject
		myAce.permission = object
		myAce.grantordeny = "DENY"
		self.getSession().add(myAce)
		self.getSession().commit()
		self.logEntry(self.LOGINFO,"ACE/DENY",str(subject),"Denied %s to %s" % (str(object),str(subject)))
	
	
	
	
	def isDenied(self,acl, subject, object):
		## 
		denied = False
		for myAce in self.getSession().query(Ace).filter(Ace.aclid==acl.id).filter(Ace.subjectid==subject).filter(Ace.permission == object).filter(Ace.grantordeny == "DENY"):
			denied = True
		return denied
		
		
		
		
		
	def isGranted(self,acl, subject, object):
		## 
		granted = False
		for myAce in self.getSession().query(Ace).filter(Ace.aclid==acl.id).filter(Ace.subjectid==subject).filter(Ace.permission == object).filter(Ace.grantordeny == "GRANT"):
			granted = True		
		return granted
	
	
	

### SRM 	
	def srmcheck(self,aclid,subject,object,minlevel=-1):
		passed = False;
		
		## Are we running in tool mode? If so, don't check security
		if self.toolMode:
			return True
			
		## If we're a sysop, we automatically get pass
		## Let's load the user's own ACL to check
		user = self.getUser(subject)
		usersAcl = self.getAcl(user.aclid)
		## The ACE is subject=user, object=SYSOP 
		if self.isGranted(usersAcl,subject,"SYSOP"):
			## User has sysop privs, let him pass
			self.logEntry(self.LOGINFO,"SRM/SYSOP/PASS",str(subject),"SYSOP: %s for %s" % (str(object),str(subject)))
			return True
			
		## Non-sysop users go by the following:
		## 1. If level is higher than minlevel then pass, otherwise...
		## 2. If GRANT exists, then pass even if we don't meet the level (+VE override)
		## 3. Unless a DENY exists, in which case you don't pass, even if 1&2 hold (-VE override)
		##
		## Should we look at the level (-1 = ignore)
		if minlevel > -1:
			## Yes we should
			if self.currentUser.accesslevel >= minlevel:
				## We're higher than the level, so we're good so far
				passed = True
				
		acl = self.getAcl(aclid)
		if not acl == None:
			## Check for any overriding grants?
			if self.isGranted(acl,subject,object):
				passed = True
			## Check for any overriding deny's?
			if self.isDenied(acl,subject,object):
				passed = False
		if passed:
			self.logEntry(self.LOGINFO,"SRM/PASS",str(subject),"PASS: %s for %s" % (str(object),str(subject)))
		else:
			self.logEntry(self.LOGINFO,"SRM/FAIL",str(subject),"FAIL: %s for %s" % (str(object),str(subject)))
		return passed
	
	


### MessageText handling
		
	def getMessagetexts(self, msgid):
		rv = []
		for msgtext in self.getSession().query(Messagetext).filter(Messagetext.messageid == msgid).order_by(Messagetext.id):	
			rv.append(msgtext.msgtext)
		return rv



		
	def deleteMessagetexts(self,msgid):
		for msgText in self.getSession().query(Messagetext).filter(Messagetext.messageid == msgid):
			self.getSession().delete(msgText)
			self.getSession().commit()
	


### Message functions



	def getTotalMessageCount(self):
		rv = self.getSession().query(Message).count()
		return rv

	## Returns the message object specified by msgid
	def getMessage(self,msgid):
		## 
		theMessage = self.getSession().query(Message).filter(Message.id == msgid)[0]
		return theMessage

		

	## Returns message ids for the board id that have been psoted since date
	## Checks security against current user if specified
	def getMessagesSince(self,board,date,checkSrm=True):
		rv = []
		for msg in self.getSession().query(Message).filter(Message.boardid == board.id).filter(Message.sentdate > date): 
			if checkSrm:
				if self.srmcheck(msg.aclid,self.currentUser.username,"READ",minlevel=board.minreadlevel):
					rv.append(msg.id)
			else:
				rv.append(msg.id)	
		return rv
			

	def getMessagesByBoardByToUsername(self,board,username,checkSrm = True):	
		rv = []
		for msg in self.getSession().query(Message).filter(Message.boardid == board.id).filter(Message.toname == username):
			if checkSrm:
				if self.srmcheck(msg.aclid,self.currentUser.username,"READ",minlevel=board.minreadlevel):
					rv.append(msg.id)
			else:
				rv.append(msg.id)	
		return rv

	## Returns message ids for the board id that have been posted by the given user
	## Checks security against current user if specified
	def getMessagesByBoardByUsername(self,board,username,checkSrm = True):	
		rv = []
		for msg in self.getSession().query(Message).filter(Message.boardid == board.id).filter(Message.fromname == username):
			if checkSrm:
				if self.srmcheck(msg.aclid,self.currentUser.username,"READ",minlevel=board.minreadlevel):
					rv.append(msg.id)
			else:
				rv.append(msg.id)	
		return rv
	
		


	## Returns all message ids for the board id 
	## Does NOT check security (why? FIXME?)
	def getMessagesByBoardid(self,boardid):
		## 
		rv = []
		for instance in self.getSession().query(Message).filter(Message.boardid == boardid).order_by(Message.sentdate): 
			rv.append(instance.id)
		return rv


	## Returns all message ids for the board NAME
	## Checks security against current user if specified
	def getMessagesByBoardname(self,name,checkSrm=True):
		## 
		board = self.getBoardByName(name)
		boardid = board.id
		rv = []
		for msg in self.getSession().query(Message).filter(Message.boardid == board.id).order_by(Message.sentdate):
			if checkSrm:
				if self.srmcheck(msg.aclid,self.currentUser.username,"READ",minlevel=board.minreadlevel):
					rv.append(msg.id)
			else:
				rv.append(msg.id)	
		return rv


					
	## Returns all message ids with to=username
	## Checks security against username if specified
	def getMessagesByUser(self,username,checkSrm=True):
		## 
		rv = []
		for instance in self.getSession().query(Message).filter(Message.toname == username).order_by(Message.sentdate): 
			if checkSrm:
				if self.srmcheck(instance.aclid,username,"READ"):
					rv.append(instance.id)
			else:
				rv.append(instance.id)	
		return rv



	def getMessagesAuthoredByUser(self,username,checkSrm=True):
		## 
		rv = []
		for instance in self.getSession().query(Message).filter(Message.fromname == username).order_by(Message.sentdate): 
			if checkSrm:
				if self.srmcheck(instance.aclid,username,"READ"):
					rv.append(instance.id)
			else:
				rv.append(instance.id)	
		return rv


	
	def getNewMessagesAllUsers(self,boardname='__pyffle_email'):
		rv = []
		board = self.getBoardByName(boardname)		
		for msg in self.getSession().query(Message).filter(Message.boardid == board.id).filter(Message.readbyrecipient == False):
			rv.append(msg.id)
		return rv
		
	## Returns all unread message ids with to=user (object)
	## Checks security against user if specified
	def getNewMessages(self,user=None,boardname='__pyffle_email',checkSrm=True):
		if user == None:
			user = self.currentUser
		rv = []
		board = self.getBoardByName(boardname)
		for msg in self.getSession().query(Message).filter(Message.boardid == board.id).filter(Message.toname == user.username).filter(Message.readbyrecipient == False):
			if checkSrm:
				if self.srmcheck(msg.aclid,user.username,"READ"):
					rv.append(msg.id)
			else:
				rv.append(msg.id)
		return rv
	


	## Marks the message read
	## Security is not checked
	def setMessageRead(self,msgid):
		theMessage = self.getMessage(msgid)
		## FIXME read receipt
		theMessage.readbyrecipient = True
		self.getSession().add(theMessage)
		self.getSession().commit()
		self.logEntry(self.LOGINFO,"READ/MESSAGE","MSGID:" + str(msgid),"Recipient read msg: %s" % (str(msgid)))




	
	## Deletes a message
	## Security is checked	
	def deleteMessage(self,msgid):
		## 
		## let's get the message first so that we can delete it's components
		msg = self.getMessage(msgid)
		if not msg == None:
			## are we allowd to delete this message? if not, error out
			## first check if it's a forum posting
			minlevel = -1
			board = self.getBoard(msg.boardid)
			
			if not board == None:
				if not board.name.startswith('__'):
					## it's a forum post, get the minimum operator level for the board
					minlevel = board.minoplevel
			
			if not self.srmcheck(msg.aclid,self.currentUser.username,"DELETE",minlevel):
				self.util.println("You are not allowed to delete this message")
				return False
			
			## now delete any text
			self.deleteMessagetexts(msgid)
			
			## remember the acl id for the step after this
			aclid = msg.aclid
			
			## delete the message itself
			self.getSession().delete(msg)
			self.getSession().commit()
			
			## finally we delete the ACL
			self.deleteAcl(aclid)
			self.logEntry(self.LOGINFO,"DELETE/MESSAGE","MSGID:" + str(msgid),"Deleted Message: %s" % (str(msgid)))
			
			return True



	## Deletes ALL messages in the system
	## Security is not checked
	def clearMessages(self):
		## 
		for instance in self.getSession().query(Message).order_by(Message.id): 
			self.util.debugln("Deleting MsgID: " + str(instance.id) + " received at " + str(instance.sentdate))
			self.deleteMessage(instance.id)




	
	## Debug function				
	def _dumpMessages(self):
	
		if True: ##self.util.DEBUG:
			for instance in self.getSession().query(Message).order_by(Message.id): 
				self.util.debugln("MsgID: " + str(instance.id) + " received at " + str(instance.sentdate))
				self.util.debugln("From: " + instance.fromname.strip())
				self.util.debugln("To: " + instance.toname.strip())
				self.util.debugln("Subj: " + instance.subject)
				self.util.debugln("--------------------------------------------------------------")
				for msgtext in self.getSession().query(Messagetext).filter(Messagetext.messageid == instance.id).order_by(Messagetext.id):
					self.util.debugln(msgtext.msgtext)
				self.util.debugln(" ")
		

				
	
	
	
	## Creates a  message (if board == __pyffle_email), with standard ACLs
	## i.e. if recipient exists locally, grant him R+D. If remote, passes to MTAs
	##
	## If board != __pyffle_email, we just post the message with an empty ACL on
	## the relevant board
	##
	## Security is not checked prior to creating - callers should establish posting/mailing
	## privs 
	def createMessage(self,fromname,toname,subject,text,board='__pyffle_email'):
		## Find the board id for the requested board
		for emailBoard in self.getSession().query(Board).filter(Board.name==board).order_by(Board.id):
			pass		
		emailId = emailBoard.id
		msgAcl = None
		## If the recipient is local, setup the permissions for this message 
		foundMTA = False
		mtaInstance = None
		if board == '__pyffle_email':
			### This is an email, let's have a look at the address
			if self.userExists(toname):
				## Got a local user, great, this will be simple
				## Create an ACL for the message now, we know the recipient is good
				msgAcl = self.createAcl()
				## Ensure the recipient can read and delete this message	
				self.grant(msgAcl,toname,"READ")
				self.grant(msgAcl,toname,"DELETE")
				self.util.debugln("Recipient can R/D: " + str(self.isGranted(msgAcl,toname,"READ")) + str(self.isGranted(msgAcl,toname,"DELETE")))
			else:
				## OK, the user is remote - let's see if anybody will accept delivery
				self.util.debugln("User not local, checking MTAs")
				for mtaName in self.mtaModules.keys():
					## Loop through our MTAs, instantiating each one until
					## we get one that accepts the address
					mta = self.mtaModules[mtaName]
					mtaInstance = mta.PyffleMta()
					mtaInstance.data = self
					mtaInstance.currentUser = self.currentUser
					if (mtaInstance.matchAddress(toname)):
						## Cool, this MTA likes the address, let's jump out of this
						self.util.debugln("Sending using " + mtaName)
						foundMTA = True
						break
						
				if foundMTA:
					## We need to create an ACL for the message's local copy
					msgAcl = self.createAcl()
				else:
					## Address doesn't appear to be valid - bork, return without sending or storing anything
					self.util.debugln("Destination address invalid, no MTA will accept destination")
	 				return None
		else:
			## Not an email, no need to deal with the addressing bruhaha above...
			## Still need an ACL though
			msgAcl = self.createAcl()
	
		## Finally build the message itself.
		## 	
		msg = Message()
		msg.fromname = fromname
		msg.toname = toname
		msg.subject = subject
	 	msg.aclid = msgAcl.id
	 	msg.boardid = emailId
	 	msg.sentdate = datetime.now()
	 	msg.readbyrecipient = False
	 	self.getSession().add(msg)
	 	self.getSession().commit()
		self.logEntry(self.LOGNORMAL,"CREATE/MESSAGE","MSGID:"+str(msg.id),"Created Message: %s" % (str(msg.id)))
			
		## Now the message text 	
	 	msgtext = Messagetext()
	 	msgtext.messageid = msg.id
	 	msgtext.aclid = msgAcl.id
	 	msgtext.msgtext = text
	 	self.getSession().add(msgtext)
	 	self.getSession().commit() 
		self.logEntry(self.LOGNORMAL,"CREATE/MESSAGETEXT","MSGTEXTID:"+str(msgtext.id),"Created Messagetext: %s" % (str(msgtext.id)))
	 	
	 	## Finally if this is an external message, pass it to the MTA
	 	if foundMTA:
	 		mtaInstance.sendMessage(msg)
			self.logEntry(self.LOGNORMAL,"SEND/MESSAGE","MSGID:"+str(msg.id),"Sent Message: %s using %s"  % (str(msg.id),str(mtaInstance.getName())))
	 		
	 	return msg.id  

