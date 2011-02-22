## Models for SqlAlchemy version 6
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref
from sqlalchemy import *
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.orm import sessionmaker
from pyffle_tables import *
from pyffle_util import *
from pyffle_data import *
from pyffle_static import *
from pyffle_editor import Editor
from datetime import datetime
import sys
import getpass
import os
import tempfile


PYFFLEVERSION = "0.01"
session = None
data = None
currentUser = None

## Load filesystem based info and STATIC
static = PyffleStatic()		## FIXME read this from a env var or something
static.parse("static")

words = {}
info = {}
help = {}
menus = {}
system = {}
text = {}
util = PyffleUtil()
words = util.loadWords("WORDS")		## FIXME should be from static
info = util.loadWords("INFO")
help = util.loadWords("HELP")
menus = util.loadWords("MENUS")
text = util.loadWords("TEXT")
system = util.loadWords("SYSTEM")

## Setup the DB connection
Session = sessionmaker()
engine = create_engine(static.options["pyffle.dburl"], echo=True) 
Session.configure(bind=engine)	
session = Session()

## Initialise tables
metadata = Base.metadata
metadata.create_all(engine)
foo = Acl()
foo = Users() 
foo = Logentry()
foo = Ace() 
foo = Board() 
foo = Message() 
foo = Messagetext() 
foo = Messageattachment() 
foo = Accesslevel() 

## Setup the data class
data = PyffleData()
data.toolMode = True 	## Turn on Tool Mode so that we override security restrictions
data.static = static
data.session = session

## Setup up the utility class
util = PyffleUtil()
util.data = data
data.util = util


data.logEntry(data.LOGCRIT,"SETUP/BEGIN","pyffle_setup","Setup started, version " + PYFFLEVERSION)
## Create a sysop user
answers = {}
answers["*NAME"] = 'system'
answers["*PASSWORD"] = 'password'
answers["*IDENTITY"] = 'System 0perator'
answers["*FIRST"] = 'Joe Q Public'
answers["*ASK BACKGROUND"] = 'I kan haz cheezburger?'

data.registerUser(answers)
sysopUser = data.getUser("system")
sysopUser.accesslevel = 9999			## FIXME configurable
sysopAcl = data.getAcl(sysopUser.aclid)
data.grant(sysopAcl,"system","SYSOP")
data.storeUser(sysopUser)

## Create internal boards
data.createBoard(		"__pyffle_email",
							"Internal Email Board",
							"system",
							"---", 
							0,
							0,
							0,None)
							
	
data.createBoard(		"__pyffle_journal",
							"Internal Journal Board",
							"system",
							"---", 
							0,
							0,
							0,None)



data.createBoard(		"__pyffle_cookie",
							"Internal Cookie Board",
							"system",
							"---", 
							0,
							0,
							0,None)

data.createBoard(		"__pyffle_plan",
							"Internal Plan Board",
							"system",
							"---", 
							0,
							0,
							0,None)
data.createBoard(		"__pyffle_pm",
							"Internal Plan Board",
							"system",
							"---", 
							0,
							0,
							0,None)
data.createBoard(		"__pyffle_chat",
							"Internal Plan Board",
							"system",
							"---", 
							0,
							0,
							0,None)
data.createBoard(		"0",
							"Sid's BBQ",
							"system",
							"---", 
							0,
							0,
							50,None)

data.createBoard(		"1",
							"Public Kremlinology",
							"system",
							"---", 
							0,
							0,
							0,None)

data.createBoard(		"comp.os.vms",
							"VMS stuff",
							"system",
							"comp.os.vms", 
							10,
							20,
							50,None)
data.createBoard(		"comp.sys.amiga",
							"Amiga, OH YEAH!",
							"system",
							"comp.sys.amiga", 
							10,
							20,
							50,None)
data.createBoard(		"uuhec.hecnet",
							"HECNET discussion",
							"system",
							"uuhec.hecnet", 
							10,
							20,
							50,None)




data.logEntry(data.LOGCRIT,"SETUP/COMPLETE","pyffle_setup","Setup complete, version " + PYFFLEVERSION)
