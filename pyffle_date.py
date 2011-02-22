## Models for SqlAlchemy version 6
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref
from sqlalchemy import *
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.orm import sessionmaker
from pyffle_tables import *
from pyffle_data import *
import pyffle_editor
from datetime import datetime
import sys
import getpass
import os
import tempfile

def getIdentity():
	return "pyffle_date v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None

	def eventDispatched(self, event):
		pass
		
	
	def go(self, command):
		self.data.util.println(datetime.now)
		