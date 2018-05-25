#!/usr/bin/env python
# coding: utf-8
# @Time     : 2018.4.8
# @Author   : Tanxiaoshu
# @File     : S0003-xunjian-windows.py
# @Library  : psutil
# @Parameter: {'cpu_percent':"50",'mem_percent':"50",'swap_mem_percent':"50",'disk_percent':"50"}

'''需要用到第三方模块psutil。脚本需要传递一个字典参数，如上parameter格式，参数需要加引号'''

import platform
import time
import socket
import json
import sys
import psutil

monitors = eval(sys.argv[1])
result = []


def ip():
	'''获取主机ip地址'''
	try:
		sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		sock.connect(('8.8.8.8',80))
		Ip = sock.getsockname()[0]
		return {'ip':{'value':Ip,'unit':0,'status':0}}
	except:
		return {'ip':{'value':0,'unit':0,'status':0}}

def os_version():
	'''获取主机类型及版本'''
	os_version = platform.platform()
	return {'os_version':{'value':os_version,'unit':0,'status':0}}

def uptime():
	'''获取运行时间'''
	run_time = psutil.boot_time()
	now_time = time.time()
	Time = (now_time - run_time) / 86400
	up_time = float("%.1f" % Time)
	return {'up_time':{'value':up_time,'unit':"day",'status':0}}

def now_time():
	'''主机当前时间'''
	nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	return {'now_time':{'value':nowtime,'unit':0,'status':0}}

def cpu():
	'''获取cpu使用率'''
	cpu_percent = psutil.cpu_percent(interval=1)
	if int(cpu_percent) > int(monitors['cpu_percent']):
		status = 1
	else:
		status = 0
	return {'cpu_percent':{'value':cpu_percent,'unit':0,'status':status}}

def process():
	'''获取进程数'''
	pids = psutil.pids()
	return {'process_num': {'value':len(pids),'unit':0,'status':0}}

def disk():
	'''获取磁盘使用率'''
	for i in psutil.disk_partitions():
		if 'cdrom' in i.opts or i.fstype == '':
			continue
		id = i.device
		for disk_name in id.split(':')[0]:
			if psutil.disk_usage(id).percent > int(monitors['disk_percent']):
				status = 1
			else:
				status = 0
			return {disk_name + "_disk_percent":{'value':psutil.disk_usage(id).percent,'unit':'%','status':status}}

def memory_total():
	'''获取内存大小'''
	mem_total = (psutil.virtual_memory().total//1024//1024)
	return {'mem_total':{'value':mem_total,'unit':'M','status':0}}

def memory_used():
	'''获取内存使用率'''
	mem_percent = psutil.virtual_memory().percent
	if int(mem_percent) > monitors['mem_percent']:
		status = 1
	else:
		status = 0
	return {'mem_percent': {'value':mem_percent,'unit':'%','status':status}}

def swap_total():
	swap_mem_total = (psutil.swap_memory().total//1024//1024)
	return {'swap_mem_total':{'value':swap_mem_total,'unit':'M','status':0}}

def swap_used():
	swap_mem_percent = psutil.swap_memory().percent
	if int(swap_mem_percent) > monitors['swap_mem_percent']:
		status = 1
	else:
		status = 0
	return {'swap_mem_percent':{'value':swap_mem_percent,'unit':'%','status':status}}

if platform.system().lower() == 'windows':
	for line in ip(),os_version(),uptime(),now_time(),cpu(),process(),disk(),\
				memory_total(),memory_used(),swap_total(),swap_used():
		result.append(line)
data = json.dumps(result,ensure_ascii=False)
print(data)

