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
import tempfile
import pyffle_module
def getIdentity():
	return "pyffle_feedback v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule(pyffle_module.PyffleModule):

	def eventDispatched(self, event):
		pass
		
	def go(self, command, args):
		self.data.stateChange("feedback_start")

		self.data.stateChange("feedback_promptstart")
		print "\nFeeeeeeeeeeeedback, man."
		confirm = self.data.util.prompt("Send note to system guru (y/n)? ")
		self.data.stateChange("feedback_promptend")

		confirm = confirm.strip()
		if confirm == "y":
			self.data.stateChange("feedback_yesstart")

			self.data.stateChange("feedback_subjectpromptstart")
			subject = self.data.util.prompt("\nSubject: ")
			self.data.stateChange("feedback_subjectpromptend")
			
			self.data.stateChange("feedback_editstart")
			editor = Editor()
			theText = editor.getText()
			self.data.stateChange("feedback_editend")

			destination = self.data.getSysopId()
			sentId = self.data.createMessage(self.currentUser.username,destination.strip(),subject.strip(),theText)
			self.data.util.println("Letter saved.")
			self.data.stateChange("feedback_sent")
			self.data.stateChange("feedback_yesend")
		else:
			self.data.stateChange("feedback_declined")
		self.data.stateChange("feedback_end")

