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
from datetime import datetime
import sys
import getpass
import os
import re

class PyffleDispatch:
	data = None
	modules = []
	modulelist = {}
		
	def setup(self,data,modules,moduleList):
		self.modules = modules
		self.data = data
		self.modulelist = moduleList

	def stateChange(self,s, args=None):
		## loop through the modules, calling each one's state() method
		for choice in self.modulelist.keys():
			chosenModule = self.modules[choice]
			pyfflePluginInstance = chosenModule.PyffleModule()
			pyfflePluginInstance.data = self.data
			if args == None:
				args = [s]
			else:
				args = [s] + args
			pyfflePluginInstance.eventDispatched(args)
