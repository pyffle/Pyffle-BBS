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

def getIdentity():
	return "pyffle_join v0.01"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None

	def eventDispatched(self, event):
		pass
		
		
		
	## UI for displaying a board list		
	def listBoards(self, boards):
		## Loop through board objects, display one numbered line / board
		self.data.stateChange("board_listboardsstart")
		self.data.util.cls()
		joinedBoardIds = self.data.getJoinedBoardids()
		self.data.util.println("\nBoards available (* = JOINed):\n")	
		i = 1
		for board in boards:
			if not board.name.startswith('__'):
				if self.data.srmcheck(board.aclid,self.currentUser.username,"READ",minlevel=board.minreadlevel):
					prefix = '   '
					if board.id in joinedBoardIds:
						prefix = ' * '
					self.data.util.println(" [^" + str(i) + "^] " + prefix + str(board.name) + " - (" + board.description + ") ") 
			i = i + 1
		self.data.stateChange("board_listboardsend")


	## UI for selecting message boards to join
	def join(self):
		self.data.stateChange("board_joinstart")

		self.data.stateChange("board_joinloopstart")
		userQuits = False
		while not userQuits:
			## Load board objects, pass them to listBoards() to display
			boards = self.data.getBoards()
			self.listBoards(boards)
			## Prompt user for board
			self.data.stateChange("board_joinpromptstart")
			choice = self.data.util.prompt("\n<Board number>, [^A^]ll, [^N^]one, [^Q^]uit    JOIN> ")	
			self.data.stateChange("board_joinpromptend")
			choice = choice.lower()
			if choice.isdigit():
				self.data.joinBoardToggle(boards[int(choice)-1].id)
			if choice == "q":
				self.data.stateChange("board_joinuserquit")
				userQuits = True		
				break
			if choice == "a":
				self.data.stateChange("board_joinall")
				self.data.joinAll()
			if choice == "n":
				self.data.stateChange("board_unjoinall")
				self.data.unjoinAll()
		

		self.data.stateChange("board_joinloopend")
		self.data.stateChange("board_joinend")
		
	def go(self, command, args):
		command = command.strip()
		if command == "join":
			self.data.stateChange("board_cmdjoinstart")
			self.join()
			self.data.stateChange("board_cmdjoinend")			
