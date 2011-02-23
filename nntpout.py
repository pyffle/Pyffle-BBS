#!/usr/bin/python
# nntptest

from nntplib import NNTP
import datetime
import os
import sys

	
args = sys.argv
if not len(args) == 2:
	print "usage nntpout.py <hostname>"
else:
	s = NNTP(args[1],user="pyffledev",password="wrhbepozv")	
	rv = s.post(sys.stdin)
	print "Server said: " + rv
