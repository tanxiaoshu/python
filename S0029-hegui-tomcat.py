#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018.5.3
# @Author   : Tanxiaoshu
# @File     : S0029-hegui-tomcat
# @Library  : 
# @Parameter: "{'link':200,'process':300,'active_process':200,'memory':1000,'cpu':50}"

import subprocess
import os
import platform
import sys
import json
import re

name = "tomcat"
result = []

def pid():
	'''判断进程'''
	cmd = "ps -ef|grep %s|grep -Ev 'grep|python'|wc -l" % name
	stdout = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read().strip()
	if int(stdout) != 0:
		cmd1 = "ps -ef|grep %s|grep -Ev 'grep|python'|awk '{print $2}'" % name
		p = subprocess.Popen(cmd1, stdout=subprocess.PIPE, shell=True).stdout.read().strip()
		return {'pid':{'value':int(p),'unit':0,'status':0}}
	else:
		return {'pid':{'value': 0, 'unit': 0, 'status': 1}}

def port():
	'''判断端口'''
	Pid = pid()['pid']
	if Pid['value'] != 0:
		cmd = "netstat -lntp|grep %s|wc -l" % Pid['value']
		stdout = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read().strip()
		if int(stdout) != 3:
			return {'port':{'value': 0, 'unit': 0, 'status': 1}}
		else:
			return {'port': {'value': stdout, 'unit': 0, 'status': 0}}
	else:
		return {'port':{'value': 0, 'unit': 0, 'status': 1}}

def link():
	'''判断连接数'''
	Pid = pid()['pid']
	if Pid['value'] == 0:
		return {'link':{'value': 0, 'unit': 0, 'status': 1}}
	else:
		cmd = "netstat an|grep ESTABLISHED|grep %s|wc -l" % name
		stdout = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read().strip()
		return {'link':{'value': stdout, 'unit': 0, 'status': 0}}

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
		if i > int(monitor['process']):
			status = 1
		else:
			status = 0
		return {'process':{'value':i,'unit':0,'status':status}}

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

def memory():
	'''获取使用内存大小'''
	Pid = pid()['pid']
	if Pid['value'] == 0:
		return {'memory':{'value': 0, 'unit': 0, 'status': 1}}
	else:
		cmd = "ps aux|grep %s|egrep -v 'python|grep'|awk '{print $6}'" % name
		stdout = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read()
		mem = int(stdout)//1024
		return {'memory':{'value': mem, 'unit': 'M', 'status': 0}}

def cpu():
	'''获取cpu使用率'''
	Pid = pid()['pid']
	if Pid['value'] == 0:
		return {'cpu_percent':{'value': 0, 'unit': 0, 'status': 1}}
	else:
		cmd = "ps aux|grep %s|grep -Ev 'grep|python'|awk '{print $3}'" % name
		std = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read().strip()
		if float(std) > monitor['cpu']:
			status = 1
		else:
			status = 0
		return {'cpu_percent':{'value':float(std),'unit':'%','status':status}}

if len(sys.argv) == 1:
	monitor = "{'link':200,'process':300,'active_process':200,'memory':1000,'cpu':50}"
else:
	monitor = eval(sys.argv[1])

if platform.system().lower() == "linux" and os.geteuid() == 0:
	for i in pid(),port(),link(),process(),active_process(),memory(),cpu():
		result.append(i)
	data = json.dumps(result,ensure_ascii=False)
	print(data)
