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

from pyffle_util import PyffleUtil


class PyffleStatic:
	## Parses a STATIC file that configures Pyffle
	
	options = {}
	util = PyffleUtil()
	def parse(self,filename):
		f = open(filename,'r')
		lines = f.readlines()
		for line in lines:
			if not (line[0] == ';' or line == ""):
				elements = line.strip().split(":")
				key = elements[0].strip()
				if not key == '':
					value = ""
				
					if len(elements) > 1:
	
						if len(elements) > 2:
							## FIXME this is retarded 
							firstItem = 1;
							lastItem = len(elements) 	
							self.util.debugln(str(firstItem) + " " + str(lastItem))
							for i in range(firstItem,lastItem):
								value = value + elements[i]
								if not i == lastItem - 1:
									value = value + ":"
						else:
							value = elements[1].strip()
						value=value.strip()
						self.options[key] = value
		self.util.debugln(str(self.options))

