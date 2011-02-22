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
	

class PyffleQuestion:
	data = None
	currentUser = None
	lastInput = ""

	def eventDispatched(self, event):
		pass


	def checkAnswer(self,question,answer):
		self.data.util.debugln("QUESTION=" + question + " ANSWER=" + answer)
		## we only care that the username is alphanumeric
		if question=="*NAME":
			if answer.isalnum():
				## check if the user exists
				if not self.data.getUser(answer.lower()):
					return True
				else:
					self.data.util.println("\nSorry, username taken. Try something else.")
					return False
			else:
				return False
		return True
			
	def askQuestions(self, questions):
		answers = {}
		for section in questions:
			ok = False
			while not ok:
				self.data.util.println(section[1])
				if section[0] == "*PASSWORD":
					matched = False
					while not matched:
						answer = self.data.util.readPassword(section[2])
						answer2 = self.data.util.readPassword("Verify: ")
						if answer == answer2:
							matched = True
						else:
							self.data.util.prompt("Password don't match, try again.")
						
				else:
					answer = self.data.util.prompt(section[2])
				
				if self.checkAnswer(section[0],answer):
					answers[section[0]] = self.data.util.printable(answer)
					ok = True
				else:
					self.data.util.println("\nErm, I didn't like that answer. There's probably an illegal character in it\n")
	
		return answers
		 
	def go(self, s):
		elements = s.split("\n")
		questions = []
		currentHeader = None
		currentText = ""
		currentPrompt = ""
		for e in elements:
			e.strip()
			if e.startswith("*"):
				## New section
				if currentHeader == None:
					## First header, store nothing
					pass
				else:
					## Second or later header, store previous
					questions.append([currentHeader,currentText,currentPrompt])
				## Reset 
				e = e.replace("\r","")
				currentHeader = e
				currentText = ""
				currentPrompt = ""
			else:
				if e.count("~"):
					e = e.replace("\r","")
					currentPrompt = e.replace("~","")
				else:
					e = e.replace("\r","")
					currentText = currentText + e + "\n"

		return self.askQuestions(questions)			