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

Base = declarative_base()	

class Acl(Base): 
	__tablename__ = 'acl'
	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
	id = Column("id",INTEGER, Sequence('aclseq'), nullable=False,index=True,unique=None,default=None, primary_key = True)
	description = Column("description", VARCHAR, nullable=True,unique=None,default=None)

class Users(Base): 
	__tablename__ = 'users'
	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
	username = Column("username", VARCHAR, nullable=False,index=True,unique=None,default=None, primary_key = True)
	fullidentity = Column("fullidentity", VARCHAR, nullable=True,unique=None,default=None)
	realname = Column("realname", VARCHAR, nullable=True,unique=None,default=None)
	phone = Column("phone", VARCHAR, nullable=True,unique=None,default=None)
	accesslevel = Column("accesslevel", INTEGER, nullable=True,unique=None,default=None)
	fakelevel = Column("fakelevel", VARCHAR, nullable=True,unique=None,default=None)
	comment = Column("comment", VARCHAR, nullable=True,unique=None,default=None)
	aclid = Column("aclid", INTEGER,ForeignKey(u'acl.id'),nullable=False,unique=None,default=None)
	password = Column("password", VARCHAR, nullable=True,unique=None,default=None)
	transferprotocol = Column("transferprotocol", VARCHAR, nullable=True,unique=None,default=None)
	timescalled = Column("timescalled", INTEGER, nullable=True,unique=None,default=None)
	kbuploaded = Column("kbuploaded", INTEGER, nullable=True,unique=None,default=None)
	kbdownloaded = Column("kbdownloaded", INTEGER, nullable=True,unique=None,default=None)
	messagesposted = Column("messagesposted", INTEGER, nullable=True,unique=None,default=None)
	datelastnewscan = Column("datelastnewscan", TIMESTAMP, nullable=True,unique=None,default=None)
	externaleditor = Column("externaleditor", VARCHAR, nullable=True,unique=None,default=None)
	consoleeditor = Column("consoleeditor", VARCHAR, nullable=True,unique=None,default=None)
	terminal = Column("terminal", VARCHAR, nullable=True,unique=None,default=None)
	pagelength = Column("pagelength", INTEGER, nullable=True,unique=None,default=None)
	disablepagedmsgs = Column("disablepagedmsgs", VARCHAR, nullable=True,unique=None,default=None)
	datefirstlogin = Column("datefirstlogin", DATE, nullable=True,unique=None,default=None)
	datefastlogin = Column("datefastlogin", DATE, nullable=True,unique=None,default=None)
	minutesontoday = Column("minutesontoday", INTEGER, nullable=True,unique=None,default=None)
	splashfile = Column("splashfile", VARCHAR, nullable=True,unique=None,default=None)

	#definition of foreignkeys backrefs
##	users_acl_rel = relation('Acl', backref='users_on_acl',primaryjoin = "Users.aclid==Acl.id",cascade="all, delete ")


class Currentlyon(Base): 
	__tablename__ = 'currentlyon'
	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
	id = Column("id", INTEGER, Sequence('currentlyon_seq'),nullable=False,index=True,unique=None,default=None, primary_key = True)
	activity = Column("activity", VARCHAR, nullable=True,unique=None,default=None)
	origin = Column("origin", VARCHAR, nullable=True,unique=None,default=None)
	username = Column("username", VARCHAR, nullable=True,unique=None,default=None)
	dateon = Column("dateon", TIMESTAMP, nullable=True,unique=None,default=None)
	pid = Column("pid", INTEGER, nullable=True,unique=None,default=None)


class Logentry(Base): 
	__tablename__ = 'logentry'
	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
	id = Column("id", INTEGER, Sequence('logentryseq'),nullable=False,index=True,unique=None,default=None, primary_key = True)
	description = Column("description", VARCHAR, nullable=True,unique=None,default=None)
	code = Column("code", VARCHAR, nullable=True,unique=None,default=None)
	subject = Column("subject", VARCHAR, nullable=True,unique=None,default=None)
	date = Column("date", TIMESTAMP, nullable=True,unique=None,default=None)
	level = Column("level", INTEGER, nullable=True,unique=None,default=None)

class Pluginsystem(Base): 
	__tablename__ = 'pluginsystem'
	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
	id = Column("id", INTEGER, Sequence('pluginsystemseq'),nullable=False,index=True,unique=None,default=None, primary_key = True)
	key = Column("key", VARCHAR, nullable=False,unique=None,default=None)
	value = Column("value", VARCHAR, nullable=True,unique=None,default=None)

class Pluginuser(Base): 
	__tablename__ = 'pluginuser'
	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
	id = Column("id", INTEGER,Sequence('pluginuserseq'), nullable=False,index=True,unique=None,default=None, primary_key = True)
	username = Column("username", VARCHAR,ForeignKey(u'users.username'),nullable=True,unique=None,default=None)
	key = Column("key", VARCHAR, nullable=False,unique=None,default=None)
	value = Column("value", VARCHAR, nullable=True,unique=None,default=None)


class Joinedboard(Base): 
	__tablename__ = 'joinedboard'
	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
	id = Column("id", INTEGER,Sequence('joinedboardseq'), nullable=False,index=True,unique=None,default=None, primary_key = True)
	username = Column("username", VARCHAR,ForeignKey(u'users.username'),nullable=False,unique=None,default=None)
	boardid = Column("boardid", INTEGER,ForeignKey(u'board.id'),nullable=False,unique=None,default=None)

	#definition of foreignkeys backrefs
##	joinedboard_board_rel = relation('Users', backref='joinedboard_on_user',primaryjoin = "Joinedboard.username==Users.username",cascade="all, delete ")
##	joinedboard_board_rel = relation('Board', backref='joinedboard_on_board',primaryjoin = "Joinedboard.boardid==Board.id",cascade="all, delete ")


class Ace(Base): 
	__tablename__ = 'ace'
	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
	id = Column("id", INTEGER,Sequence('aceseq'), nullable=False,unique=None,index=True,default=None, primary_key = True)
	aclid = Column("aclid", INTEGER,ForeignKey(u'acl.id'),nullable=False,unique=None,default=None)
	subjectid = Column("subjectid", VARCHAR,ForeignKey(u'users.username'),nullable=True,unique=None,default=None)
	permission = Column("permission", VARCHAR, nullable=True,unique=None,default=None)
	grantordeny = Column("grantordeny", VARCHAR, nullable=True,unique=None,default=None)

	#definition of foreignkeys backrefs
##	ace_acl_rel = relation('Acl', backref='ace_on_acl',primaryjoin = "Ace.aclid==Acl.id",cascade="all, delete ")
##	ace_users_rel = relation('Users', backref='ace_on_users',primaryjoin = "Ace.subjectid==Users.username",cascade="all, delete ")

class Board(Base): 
	__tablename__ = 'board'
	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
	id = Column("id", INTEGER,Sequence('boardseq'), nullable=False,index=True,unique=None,default=None, primary_key = True)
	name = Column("name", VARCHAR, nullable=True,unique=None,default=None)
	aclid = Column("aclid", INTEGER,ForeignKey(u'acl.id'),nullable=False,unique=None,default=None)
	description = Column("description", VARCHAR, nullable=True,unique=None,default=None)
	owner = Column("owner", VARCHAR, nullable=True,unique=None,default=None)
	externalname = Column("externalname", VARCHAR, nullable=True,unique=None,default=None)
	minreadlevel = Column("minreadlevel", INTEGER, nullable=True,unique=None,default=None)
	minpostlevel = Column("minpostlevel", INTEGER, nullable=True,unique=None,default=None)
	minoplevel = Column("minoplevel", INTEGER, nullable=True,unique=None,default=None)

	#definition of foreignkeys backrefs
##	board_acl_rel = relation('Acl', backref='board_on_acl',primaryjoin = "Board.aclid==Acl.id",cascade="all, delete ")

class Message(Base): 
	__tablename__ = 'message'
	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
	id = Column("id", INTEGER,Sequence('messageseq'), nullable=False,index=True,unique=None,default=None, primary_key = True)
	aclid = Column("aclid", INTEGER,ForeignKey(u'acl.id'),nullable=False,unique=None,default=None)
	messagetype = Column("messagetype", VARCHAR, nullable=True,unique=None,default=None)
	fromname = Column("fromname", VARCHAR, nullable=True,unique=None,default=None)
	toname = Column("toname", VARCHAR, nullable=True,unique=None,default=None)
	subject = Column("subject", VARCHAR, nullable=True,unique=None,default=None)
	sentdate = Column("sentdate", TIMESTAMP, nullable=True,unique=None,default=None)
	boardid = Column("boardid", INTEGER,ForeignKey(u'board.id'),nullable=True,unique=None,default=None)
	readbyrecipient = Column("readbyrecipient", BOOLEAN, nullable=True,unique=None,default=None)
	receiptrequested = Column("receiptrequested", BOOLEAN, nullable=True,unique=None,default=None)

	#definition of foreignkeys backrefs
	#boardid = Column("boardid", INTEGER,ForeignKey(u'board.id'),nullable=False,unique=None,default=None)
##	message_acl_rel = relation('Acl', backref='message_on_acl',primaryjoin = "Message.aclid==Acl.id",cascade="all, delete ")
##	message_board_rel = relation('Board', backref='message_on_board',primaryjoin = "Message.boardid==Board.id",cascade="all, delete ")

class Messagetext(Base): 
	__tablename__ = 'messagetext'
	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
	id = Column("id", INTEGER, Sequence('messagetextseq'),nullable=False,index=True,unique=None,default=None, primary_key = True)
	messageid = Column("messageid", INTEGER,ForeignKey(u'message.id'),nullable=False,unique=None,default=None)
	aclid = Column("aclid", INTEGER,ForeignKey(u'acl.id'),nullable=False,unique=None,default=None)
	msgtext = Column("msgtext", VARCHAR, nullable=True,unique=None,default=None)

	#definition of foreignkeys backrefs
##	messagetext_message_rel = relation('Message', backref='messagetext_on_message',primaryjoin = "Messagetext.messageid==Message.id",cascade="all, delete ")
##	messagetext_acl_rel = relation('Acl', backref='messagetext_on_acl',primaryjoin = "Messagetext.aclid==Acl.id",cascade="all, delete ")

class Messageattachment(Base): 
	__tablename__ = 'messageattachment'
	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
	id = Column("id", INTEGER, Sequence('messageattachmentseq'),nullable=False,index=True, unique=None,default=None, primary_key = True)
	messageid = Column("messageid", INTEGER,ForeignKey(u'message.id'),nullable=False,unique=None,default=None)
	aclid = Column("aclid", INTEGER,ForeignKey(u'acl.id'),nullable=False,unique=None,default=None)
	name = Column("name", VARCHAR, nullable=True,unique=None,default=None)
	description = Column("description", VARCHAR, nullable=True,unique=None,default=None)
	mimetype = Column("mimetype", VARCHAR, nullable=True,unique=None,default=None)
	contents = Column("contents", VARCHAR, nullable=True,unique=None,default=None)

	#definition of foreignkeys backrefs
##	messageattachment_message_rel = relation('Message', backref='messageattachment_on_message',primaryjoin = "Messageattachment.messageid==Message.id",cascade="all, delete ")
##	messageattachment_acl_rel = relation('Acl', backref='messageattachment_on_acl',primaryjoin = "Messageattachment.aclid==Acl.id",cascade="all, delete ")

#class Lastreadpointer(Base): 
#	__tablename__ = 'lastreadpointer'
#	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
#	userid = Column("userid", VARCHAR,ForeignKey(u'users.username'),nullable=True,unique=None,default=None)
#	boardid = Column("boardid", INTEGER,ForeignKey(u'board.id'),nullable=False,unique=None,default=None)
#	highestread = Column("highestread", INTEGER, nullable=False,unique=None,default=None)

	#definition of foreignkeys backrefs
#	lastreadpointer_users_rel = relation('Users', backref='lastreadpointer_on_users',primaryjoin = "Lastreadpointer.userid==Users.username")
 #   lastreadpointer_board_rel = relation('Board', backref='lastreadpointer_on_board',primaryjoin = "Lastreadpointer.boardid==Board.id")

class Accesslevel(Base): 
	__tablename__ = 'accesslevel'
	__table_args__ = {'useexisting':True,'sqlite_autoincrement':True}
	id = Column("id", INTEGER, Sequence('accesslevelseq'),nullable=False,index=True, unique=None,default=None, primary_key = True)
	timeallowed = Column("timeallowed", INTEGER, nullable=True,unique=None,default=None)
	downloadkb = Column("downloadkb", INTEGER, nullable=True,unique=None,default=None)
	uploadkb = Column("uploadkb", INTEGER, nullable=True,unique=None,default=None)

