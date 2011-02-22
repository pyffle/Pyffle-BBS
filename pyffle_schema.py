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
static.parse("/pyffle/static")

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
foo = Currentlyon() 
foo = Pluginsystem() 
foo = Pluginuser() 

