#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018.4.19
# @Author   : Tanxiaoshu
# @File     : S0010-sunjian-nginx
# @Library  :
# @Parameter:

import json
import sys
import subprocess
import re
import os
import platform
import socket

result = []
name = 'nginx'


def pid():
	'''获取pid'''
	try:
		cmd = "ps -ef|grep %s|grep -Ev 'grep|python'|wc -l" % name
		pid = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read()
		if int(pid) == 0:
			return {'pid':{'value':0,'unit':0,'status':1}}
		else:
			cmd1 = "ps -ef|grep %s|grep -Ev 'grep|python'|awk 'NR==1 {print $2}'" % name
			pid1 = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE).stdout.read().split('\n')
			return {'pid':{'value':pid1[0],'unit':0,'status':0}}
	except:
		return {'pid':{'value':0,'unit':0,'status':1}}

def server_name():
	'''获取name'''
	try:
		cmd = "ps -ef|grep %s|grep -Ev 'grep|python'|wc -l" % name
		pid = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read()
		if int(pid) == 0:
			return {'name':{'value':name,'unit':0,'status':1}}
		else:
			return {'name':{'value':name,'unit':0,'status':0}}
	except:
		return {'name': {'value': name, 'unit': 0, 'status': 1}}

def ip():
	'''获取ip地址'''
	try:
		sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		sock.connect(('8.8.8.8',80))
		Ip = sock.getsockname()[0]
		return {'ip':{'value':Ip,'unit':0,'status':0}}
	except:
		return {'ip':{'value':0,'unit':0,'status':1}}

def port():
	'''获取端口'''
	p = pid()['pid']
	if p['value'] == 0:
		return {'port':{'value':0,'unit':0,'status':1}}
	else:
		cmd = "netstat -lntp|grep -v tcp6|grep %s" % p['value']
		stdout = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read()
		Port = re.search('^.*:(\d+)',stdout).group(1)
		return {'port':{'value':Port,'unit':0,'status':0}}

# def status():
# 	Port = port()
# 	if Port != "" and Port != None:
# 		service['status'] = "running"
# 	else:
# 		service['status'] = "down"
# 	# print(service['status'])
# 	return service['status']

def link():
	'''获取连接数'''
	Port = port()['port']
	if  Port['value'] == 0:
		return {'link':{'value':0,'unit':0,'status':1}}
	else:
		cmd = "netstat -an|grep 'ESTABLISHED'|grep %s|wc -l" % Port['value']
		Link = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE).stdout.read().split('\n')
		return {'link':{'value':Link[0],'unit':0,'status':0}}

def memory():
	'''获取内存使用率'''
	Pid = pid()['pid']
	if Pid['value'] == 0:
		return {'memory':{'value':0,'unit':'M','status':1}}
	else:
		cmd = "cat /proc/%s/status|grep VmRSS|tr -cd '[0-9]'" % Pid['value']
		stdout = subprocess.Popen(cmd % Pid,shell=True,stdout=subprocess.PIPE).stdout.read()
		mem = int(stdout)//1024
		return {'memory':{'value':mem,'unit':'M','status':0}}

def cpu():
	'''获取cpu使用率'''
	Pid = pid()['pid']
	if Pid['value'] == 0:
		return {'cpu_percent': {'value': 0, 'unit': 'M', 'status': 1}}
	else:
		cmd = "top -n1 -p %s|grep %s|awk '{cpu=NF-4} {print $cpu}'" % (Pid['value'],name)
		stdout = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read().strip()
		return {'cpu_percent':{'value':stdout,'unit':'M','status':0}}

if platform.system().lower() == "linux" and os.getuid() == 0:
	for i in pid(),server_name(),ip(),port(),link(),memory(),cpu():
		result.append(i)
	date = json.dumps(result,ensure_ascii=False)
	print(date)

