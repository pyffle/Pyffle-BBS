## nntptest

from nntplib import NNTP
import datetime
import os
import sys
#servers = ["news.mi.ras.ru",
#"news.grnet.gr", 				
#"freenews.netfront.net", 		
#"textnews.news.cambrium.nl", 	
#"news.siol.net", 				
#"news.upc.ie", 				
#"news.task.gda.pl", 			
#"rutherfordium.club.cc.cmu.ede",
#"test.news.mediaways.net", 	 
#"snorky.mixmin.net"] 			

servers = [["news.mi.ras.ru",[],["comp.sys.amiga","comp.os.vms","alt.test"]]]
rnews = "rnews"
def feedPost(article):
	head1 = s.head(article)
	lines = head1[3]
	outmsg =  ""
	for line in lines:
		outmsg = outmsg +  str(line) + "\n"
	outmsg = outmsg +   "\n" 
	msg1=  s.body(article)
	lines = msg1[3]
	for line in lines:
		outmsg = outmsg +  str(line) + "\n"
	mailin = os.popen(rnews,"w")
	mailin.write(outmsg)
	mailin.close()	

def feedGroup(server,groupName,lastread,seen):
	date = lastread.strftime("%y%m%d")
	time = lastread.strftime("%H%M%S")
	resp,articles = s.newnews(groupName,date,time)
	max = len(articles)
	print groupName + " has " + str(max)
	i = 0
	for article in articles:
		i = i + 1
		if not article in seen:
			print " Postinng: " + server + " (%s/%s) " % (str(i),str(max))  + "  %s" % (str(article)) 
			feedPost(article)
			seen.append(article)
		else:
			print "\nSeen: " + article
import pickle

def loadLastread():
	rv = None
	if True:			## FIXME chcek for file
		f = open('/pyffle/data/pyffle.nntp.lastread', 'r+')
		rv = pickle.load(f)
		f.close()
	else:
		rv = datetime.datetime(2011,02,21)			
		

	f = open('/pyffle/data/pyffle.nntp.seen', 'r+')
	seen = pickle.load(f)
	f.close()


	return rv,seen

def resetLastread():
	storeLastread(datetime.datetime(2011,02,21),[])	
	
	
def storeLastread(date,seen):
	f = open('/pyffle/data/pyffle.nntp.lastread', 'w')
	pickle.dump(date, f)
	f.close()

	f = open('/pyffle/data/pyffle.nntp.seen', 'w')
	pickle.dump(seen, f)
	f.close()
	
args = sys.argv
if len(args) == 2:
	print "Resetting lastread and seen.."
	resetLastread()
	exit 

seen = []
newdate = None
print "Reading date and seen files"
date,seen = loadLastread()

for serverentry in servers:
		server = serverentry[0]
		newsgroups = serverentry[2]
		print "Connecting to: " + server	
		s = NNTP(server)	
		for newsgroup in newsgroups:
			feedGroup(server, newsgroup, date, seen)		
	
		serverdate = s.date()
		date = serverdate[1]
		time = serverdate[2]
		year = 2000 + int(serverdate[1][0:2])   ## So I got a Y3K problem here. Deal.
		month = int(serverdate[1][2:4])
		day = int(serverdate[1][4:])
		hour = int(serverdate[2][0:2])   
		minute = int(serverdate[2][2:4])
		second = int(serverdate[2][4:])
		
		newdate = datetime.datetime(year,month,day,hour,minute,second)
		print "Server time is " + str(newdate)
if not newdate == None:
	print "Got a new server time, storing that"
else:
	newdate = date
print "Writing date and seen files"
storeLastread(newdate,seen)
