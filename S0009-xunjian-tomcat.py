#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018.4.23
# @Author   : Tanxiaoshu
# @File     : S0009-xunjian-tomcat
# @Library  : 
# @Parameter:

import sys
import platform
import socket
import subprocess
import os
import re
import json

result = []
name = 'tomcat'

def ip():
	'''获取ip地址'''
	try:
		sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		sock.connect(('8.8.8.8',80))
		ip = sock.getsockname()[0]
		return {'ip':{'value':ip,'unit':0,'status':0}}
	except:
		return {'ip':{'value':0,'unit':0,'status':1}}

def pid():
	'''获取pid'''
	try:
		cmd = "ps -ef|grep %s|grep -Ev 'grep|python'|wc -l" % name
		st = subprocess.Popen([cmd],shell=True,stdout=subprocess.PIPE).stdout.read().strip()
		if int(st) == 0:
			return {'pid':{'value':0,'unit':0,'status':1}}
		else:
			cmd1 = "ps -ef|grep %s|grep -Ev 'grep|python'|awk '{print $2}'" % name
			st1 = subprocess.Popen([cmd1], shell=True, stdout=subprocess.PIPE).stdout.read().strip()
			return {'pid':{'value':st1,'unit':0,'status':0}}
	except:
		return {'pid':{'value':0,'unit':0,'status':1}}

def server_name():
	'''获取server name'''
	try:
		cmd = "ps -ef|grep %s|grep -Ev 'grep|python'|wc -l" % name
		st = subprocess.Popen([cmd],shell=True,stdout=subprocess.PIPE).stdout.read().strip()
		if int(st) == 0:
			return {name:{'value':0,'unit':0,'status':1}}
		else:
			cmd1 = "ps -ef|grep %s|grep -Ev 'grep|python'|awk '{print $2}'" % name
			st1 = subprocess.Popen([cmd1], shell=True, stdout=subprocess.PIPE).stdout.read().strip()
			return {name:{'value':name,'unit':0,'status':0}}
	except:
		return {name:{'value':0,'unit':0,'status':1}}

def port():
	'''获取端口'''
	Port = []
	Pid = pid()['pid']
	if Pid['value'] == 0:
		return {'port':{'value':0,'unit':0,'status':1}}
	else:
		cmd = "netstat -lntp|grep " + Pid['value']
		port = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read()
		for i in port.split('\n'):
			p = re.search("^tcp.*:(\d+)",i)
			if p:
				Port.append(p.group(1))
		return {'port':{'value':Port,'unit':0,'status':0}}

def memory():
	'''获取内存使用率'''
	try:
		cmd = "ps aux|grep %s|egrep -v 'python|grep'|awk '{print $6}'" % name
		stdout = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read()
		mem = int(stdout)//1024
		return {'memory':{'value':mem,'unit':0,'status':0}}
	except:
		return {'memory':{'value':0,'unit':0,'status':1}}

def process():
	'''获取总线程数'''
	Pid = pid()['pid']
	if Pid['value'] == 0:
		return {'process':{'value':0,'unit':0,'status':1}}
	else:
		cmd = "ps -Lf %s" % Pid['value']
		stdout = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read()
		i = 0
		for line in stdout.split('\n'):
			i +=1
		return {'process':{'value':i,'unit':0,'status':0}}

def active_process():
	'''获取活动线程数'''
	Pid = pid()['pid']
	if Pid['value'] == 0:
		return {'active_process':{'value':0,'unit':0,'status':1}}
	else:
		cmd = "ps -Lf %s" % Pid['value']
		stdout = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read()
		i = 0
		for line in stdout.split('\n'):
			line = re.search("R|R\+",line)
			if line:
				i +=1
		return {'active_process':{'value':i,'unit':0,'status':0}}

def silent_process():
	'''获取空闲线程数'''
	Pid = pid()['pid']
	if Pid['value'] == 0:
		return {'silent_process':{'value':0,'unit':0,'status':1}}
	else:
		cmd = "ps -Lf %s" % Pid['value']
		stdout = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read()
		i = 0
		for line in stdout.split('\n'):
			line = re.search("S\w",line)
			if line:
				i +=1
		return {'silent_process':{'value':i,'unit':0,'status':0}}


if platform.system().lower() == "linux" and os.getuid() == 0:
	for i in ip(),pid(),server_name(),port(),memory(),process(),active_process(),silent_process():
		result.append(i)
	date = json.dumps(result,ensure_ascii=False)
	print(date)
