#!/usr/bin/python
# nntptest

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

	
args = sys.argv
if not len(args) == 2:
	print "usage nntpout.py <hostname>"
else:
	s = NNTP(args[1],user="pyffledev",password="wrhbepozv")	
	rv = s.post(sys.stdin)
	print "Server said: " + rv
