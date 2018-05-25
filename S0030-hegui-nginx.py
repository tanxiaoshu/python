#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018.5.3
# @Author   : Tanxiaoshu
# @File     : S0030-hegui-nginx
# @Library  : 
# @Parameter: "{'link':1000,'memory':1000,'cpu':50}"

import subprocess
import os
import platform
import sys
import json

name = "nginx"
result = []

def pid():
	'''判断进程'''
	cmd = "ps -ef|grep %s|grep -Ev 'grep|python'|wc -l" % name
	stdout = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).stdout.read().strip()
	if int(stdout) == 0:
		status = 1
	else:
		status = 0
	return {'pid':{'value':stdout,'unit':0,'status':status}}

def port():
	'''判断端口'''
	cmd = "netstat -lntp|grep %s|wc -l" % name
	stdout = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read().strip()
	if int(stdout) == 0:
		status = 1
	else:
		status = 0
	return {'port':{'value': stdout, 'unit': 0, 'status': status}}

def link():
	'''判断连接数'''
	Pid = pid()['pid']
	if int(Pid['value']) == 0:
		return {'link':{'value': 0, 'unit': 0, 'status': 1}}
	else:
		cmd = "netstat an|grep ESTABLISHED|grep %s|wc -l" % name
		stdout = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read().strip()
		if int(stdout) > monitor['link']:
			status = 1
		else:
			status = 0
		return {'link':{'value': stdout, 'unit': 0, 'status': status}}

def memory():
	'''获取memory使用率'''
	Pid = pid()['pid']
	if int(Pid['value']) == 0:
		return {'memory':{'value':0,'unit':'M','status':1}}
	else:
		cmd1 = "ps -ef|grep %s|grep -Ev 'grep|python'|grep master|awk '{print $2}'" % name
		Pid = subprocess.Popen(cmd1,shell=True,stdout=subprocess.PIPE).stdout.read()
		cmd = "cat /proc/%s/status|grep VmRSS|tr -cd '[0-9]'" % int(Pid)
		stdout = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read()
		mem = int(stdout)//1024
		if mem > monitor['memory']:
			status = 1
		else:
			status = 0
		return {'memory':{'value':mem,'unit':'M','status':status}}

def cpu():
	'''获取cpu使用率'''
	Pid = pid()['pid']
	if int(Pid['value']) == 0:
		return {'cpu_percent':{'value': 0, 'unit': '%', 'status': 1}}
	else:
		cmd = "ps aux|grep %s|grep -Ev 'grep|python'|awk '{print $3}'" % name
		std = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read().strip().split('\n')
		cpu_percent = 0
		for i in std:
			i = float(i)
			cpu_percent = i + cpu_percent
		if cpu_percent > monitor['cpu']:
			status = 1
		else:
			status = 0
		return {'cpu_percent':{'value':cpu_percent,'unit':'%','status':status}}

if len(sys.argv) == 1:
	monitor = "{'link':1000,'memory':1000,'cpu':50}"
else:
	monitor = sys.argv[1]

if platform.system().lower() == "linux" and os.geteuid() == 0:
	for i in pid(),port(),link(),memory(),cpu():
		result.append(i)
	data = json.dumps(result,ensure_ascii=False)
	print(data)
