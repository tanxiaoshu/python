#!/usr/bin/env python
# -*- coding: utf-8 -*-
#author:TanXiaoshu
#date:2018.4.3

import re
import time

def net_status(eth):
	with open('/proc/net/dev','r') as f:
		for line in f.readlines()[2:]:
			if re.search(eth,line):
				con = line.split()
				receive_old = int(con[1])
				tramsmit_old = int(con[10])
	time.sleep(10)
	with open('/proc/net/dev','r') as f:
		for line in f.readlines()[2:]:
			if re.search(eth,line):
				con = line.split()
				receive_new = int(con[1])
				tramsmit_new = int(con[10])

	receive_speed = (receive_new - receive_old)*8/1024/1024
	tramsmit_speed = (tramsmit_new - tramsmit_old)*8/1024/1024
	print(float("%.2f" % receive_speed))
	print(float("%.2f" % tramsmit_speed))

net_status("enp0s20f0u9")