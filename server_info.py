#!/usr/bin/env python
# coding: utf-8
# @Time     : 2018.4.8
# @Author   : Tanxiaoshu
# @File     : server_info.py
# @Library  : install psutil,
# @Parameter: {'cpu_percent':"50",'mem_percent':"50",'swap_mem_percent':"50",'disk_percent':"50"}

'''需要用到第三方模块psutil。脚本需要传递一个字典参数，如上parameter格式，参数需要加引号'''

import platform
import time
import socket
import subprocess
import re
import os
import multiprocessing
from collections import namedtuple
import json
import sys
import psutil
import datetime

monitors = eval(sys.argv[1])
result = {}

if platform.system().lower() == 'linux':
	def ip():
		'''获取主机IP地址'''
		try:
			sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			sock.connect(('8.8.8.8',80))
			Ip = sock.getsockname()[0]
			result['ip'] = {'value':Ip,'unit':' ','status':0}
			#print(result['ip'])
			return result['ip']
		except:
			result['ip'] = None
			return result['ip']

	def os_version():
		'''获取主机类型及版本'''
		os = platform.system()
		result['system_type'] = {'value':os,'unit':' ','status':0}
		osversion = platform.uname()[2]
		result['system_version'] = {'value':osversion,'unit':' ','status':0}
		return result['system_type'],result['system_version']

	def uptime():
		'''主机运行时间'''
		with open("/proc/uptime") as f:
			for line in f:
				up_time = float(line.split()[0].split(".")[0]) / 86400
				os_uptime = float("%.1f" % up_time)
				result['os_uptime'] = {'value':os_uptime,'unit':'day','status':0}
				# print(result['os_uptime'])
				return result['os_uptime']

	def now_time():
		'''主机当前时间'''
		nowtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
		result['now_time'] = {'value':nowtime,'unit':' ','status':0}
		return result['now_time']


	def lv():
		'''主机LVM状态'''
		try:
			res = subprocess.Popen(['lvdisplay'], stdout=subprocess.PIPE, shell=True)
			stdout = res.stdout
			# print(stdout)
			lv_status = []
			for line in stdout.readlines():
				# print(line)
				if re.search('LV Status', line):
					stat = line.split()[2]
					if stat == "NOT available":
						lv_status.append(stat)
			if len(lv_status) > 0:
				status = 1
			else:
				status = 0
			result['lv_status'] = {'value':len(lv_status),'unit':' ','status':status}
			return result['lv_status']
		except:
			result['lv_status'] = None

	def message_log():
		'''主机message日志巡检'''
		month = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'June', '07': 'July', '08': 'Aug', '09': 'Sept', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
		try:
			os_month = time.strftime("%m", time.localtime())
			os_day = re.search('[1-9].?', time.strftime("%d", time.localtime())).group()
			if int(os_day) < 10:
				day = month[os_month] + '  ' + os_day
			else:
				day = month[os_month] + ' ' + os_day

			with open('/var/log/messages', 'r') as f:
				i = 0
				for line in f:
					# print(line)
					if re.search(r'%s.*(Error|error)' % (day), line):
						i += 1
				if i > 0:
					status = 1
				else:
					status = 0
				result['message_log'] = {'value':i,'unit':' ','status':status}
			return result['message_log']
		except:
			result['message_log'] = None
			return result['message_log']

	def dmesg_log():
		'''主机dmesg日志巡检'''
		try:
			with open('/var/log/dmesg', 'r') as f:
				i = 0
				for line in f:
					# print(line)
					if re.search(r'(Error|error)', line):
						i += 1
				if i > 0:
					status = 1
				else:
					status = 0
				result['dmesg_log'] = {'value':i,'unit':' ','status':status}
			return result['dmesg_log']
		except:
			result['dmesg_log'] = None
			return result['dmesg_log']

	def cpu():
		'''获取主机CPU状态及使用率'''
		result['cpu_core'] = multiprocessing.cpu_count()
		cmd1 = subprocess.Popen('cat /proc/stat|grep -w cpu', shell=True, stdout=subprocess.PIPE)
		cpu_info1 = cmd1.stdout.read().strip().split()
		cpu_used1 = int(cpu_info1[1])
		total1 = int(cpu_info1[1]) + int(cpu_info1[2]) + int(cpu_info1[3]) + int(cpu_info1[4]) + int(cpu_info1[5]) + int(cpu_info1[6]) + int(cpu_info1[7])
		time.sleep(1)
		cmd2 = subprocess.Popen('cat /proc/stat|grep -w cpu', shell=True, stdout=subprocess.PIPE)
		cpu_info2 = cmd2.stdout.read().strip().split()
		cpu_used2 = int(cpu_info2[1])
		total2 = int(cpu_info2[1]) + int(cpu_info2[2]) + int(cpu_info2[3]) + int(cpu_info2[4]) + int(cpu_info2[5]) + int(cpu_info2[6]) + int(cpu_info2[7])
		cpu_idel = cpu_used2 - cpu_used1
		total = total2 - total1
		cpu_used = cpu_idel * 100 // total
		# cpu_result['cpu_used'] = cpu_used
		if int(cpu_used) > int(monitors['cpu_percent']):
			status = 1
		else:
			status = 0
		result['cpu'] = {'value':cpu_used,'unit':'%','status':status}
		# print(result['cpu_status'])
		return result['cpu']

	def process():
		'''获取主机进程数'''
		stdout = subprocess.Popen('ps -ef|wc -l',shell=True,stdout=subprocess.PIPE).stdout.read().strip()
		p = stdout
		result['process'] = {'value':p,'unit':" ",'status':0}
		return result['process']

	def process_zombie():
		'''获取主机僵尸进程数'''
		stdout = subprocess.Popen('top -n1|head -2|tail -1', shell=True, stdout=subprocess.PIPE).stdout.read().strip()
		#zombie = re.search(r'stopped,\s*?([0-9]).*zombie',stdout)
		zombie = re.split('\s+',stdout)
		z = zombie[-2]
		if z > 0:
			status = 1
		else:
			status = 0
		result['zombie'] = {'value':z,'unit':' ','status':status}
		#print(result['zombie'])
		return result['zombie']


	#巡检磁盘
	disk_ntuple = namedtuple('partition', 'device mountpoint fstype')
	usage_ntuple = namedtuple('usage', 'total used free percent')  # 获取当前操作系统下所有磁盘

	def disk_partitions(all=False):
		# 获取文件系统及所使用的分区
		"""Return all mountd partitions as a nameduple. 
		If all == False return phyisical partitions only. 
		"""
		phydevs = []
		f = open("/proc/filesystems", "r")
		for line in f:
			if not line.startswith("nodev"):
				phydevs.append(line.strip())
		# print(phydevs)
		f.close()

		retlist = []
		f = open('/etc/mtab', "r")
		for line in f:
			if not all and line.startswith('none'):
				continue
			fields = line.split()
			device = fields[0]
			mountpoint = fields[1]
			# print(mountpoint)
			fstype = fields[2]
			# print(line)
			if not all and fstype not in phydevs:
				continue
			if device == 'none':
				device = ''
			ntuple = disk_ntuple(device, mountpoint, fstype)
			retlist.append(ntuple)
		f.close
		# print(retlist)
		return retlist

	def disk_usage(path):
		# 统计某磁盘使用情况，返回对象
		"""Return disk usage associated with path."""
		st = os.statvfs(path)
		free = (st.f_bavail * st.f_frsize)
		total = (st.f_blocks * st.f_frsize)
		used = (st.f_blocks - st.f_bfree) * st.f_frsize
		try:
			percent = (float(used) / total) * 100
		except ZeroDivisionError:
			percent = 0
		return usage_ntuple(total, used, free, int(percent))

	def disk():
		for i in disk_partitions():
			# 获取磁盘使用率
			# print(i[1])
			value = list(disk_usage(i[1]))
			if int(value[3]) < monitors['disk_percent']:
				status = 0
			else:
				status = 1
			result[i[1]] = {'value':value[3],'unit':'%','status':status}

	def mem_info():
		'''获取内存大小，使用率等'''
		meminfo = {}
		with open('/proc/meminfo') as f:
			for line in f:
				meminfo[line.split(':')[0]] = int(line.split(':')[1].strip().split()[0])
		mem_total = int(meminfo['MemTotal']) // 1024
		result['mem_total'] = {'value':mem_total,'unit':'M','status':0}
		mem_used = (int(meminfo['MemTotal']) - int(meminfo['MemFree']) - int(meminfo['Buffers']) - int(meminfo['Cached'])) // 1024
		result['mem_used'] = {'value':mem_used,'unit':'M','status':0}
		mem_used_percent = int(mem_used) * 100 // int(mem_total)
		if mem_used_percent > monitors['mem_percent']:
			status = 1
		else:
			status = 0
		result['mem_used_percent'] = {'value':mem_used_percent,'unit':'%','status':status}

	def swap():
		'''获取swap大小及使用率等'''
		with open('/proc/meminfo','r') as f:
			for line in f:
				if line.startswith('SwapTotal'):
					swaptotal = line.split()[1]
					result['swaptotal'] = {'value':int(swaptotal) // 1024,'unit':"M",'status':0}
					#print(swaptotal)
				elif line.startswith('SwapFree'):
					swapfree = line.split()[1]
					#print(swapfree)
			swap_used = (int(swaptotal) - int(swapfree)) // int(swaptotal) * 100
			if swap_used > 0:
				status = 1
			else:
				status = 0
			result['swap_used_percent'] = {'value':swap_used,'unit':'%','status':status}
			return result['swap_used_percent']


elif platform.system().lower() == 'windows':
	def ip():
		'''获取主机ip地址'''
		try:
			sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			sock.connect(('8.8.8.8',80))
			Ip = sock.getsockname()[0]
			result['ip'] = Ip
			#print(result['ip'])
			return result['ip']
		except:
			result['ip'] = None
			return result['ip']

	def os_version():
		'''获取主机类型及版本'''
		result['os_version'] = platform.platform()
		return result['os_version']

	def uptime():
		'''获取运行时间'''
		run_time = psutil.boot_time()
		now_time = time.time()
		Time = (now_time - run_time) / 86400
		up_time = str(float("%.1f" % Time)) + "day"
		result['up_time'] = up_time

	def now_time():
		'''主机当前时间'''
		result['now_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
		return result['now_time']

	def cpu():
		'''获取cpu使用率'''
		cpu_percent = psutil.cpu_percent(interval=1)
		result['cpu_percent'] = cpu_percent
		if int(cpu_percent) > int(monitors['cpu_percent']):
			result['cpu_status'] = '异常'.decode('utf-8')
		else:
			result['cpu_status'] = '正常'.decode('utf-8')
		# print(type(result['cpu_status']))
		# print(result['cpu_status'])
		return (result['cpu_percent'],result['cpu_status'])

	def process():
		'''获取进程数'''
		pids = psutil.pids()
		result['process_num'] = len(pids)
		return result['process_num']

	def disk():
		'''获取磁盘使用率'''
		for i in psutil.disk_partitions():
			if 'cdrom' in i.opts or i.fstype == '':
				continue
			id = i.device
			for disk_name in id.split(':')[0]:
				result[disk_name + "_disk_percent"] = psutil.disk_usage(id).percent
				if int(result[disk_name + "_disk_percent"]) > int(monitors['disk_percent']):
					result[disk_name + '_disk_status'] = '异常'.decode('utf-8')
				else:
					result[disk_name + '_disk_status'] = '正常'.decode('utf-8')
			# print(result[disk_name + '_status'])

	def memory():
		'''获取内存'''
		mem_total = (psutil.virtual_memory().total//1024//1024)
		mem_percent = psutil.virtual_memory().percent
		result['mem_total'] = str(mem_total) + "M"
		result['mem_percent'] = mem_percent
		if int(mem_percent) > monitors['mem_percent']:
			result['mem_status'] = '异常'.decode('utf-8')
		else:
			result['mem_status'] = '正常'.decode('utf-8')

	def swap_mem():
		swap_mem_total = (psutil.swap_memory().total//1024//1024)
		swap_mem_percent = psutil.swap_memory().percent
		result['swap_mem_total'] = str(swap_mem_total) + "M"
		result['swap_mem_percent'] = swap_mem_percent
		if int(swap_mem_percent) > monitors['swap_mem_percent']:
			result['swap_mem_status'] = '异常'.decode('utf-8')
		else:
			result['swap_mem_status'] = '正常'.decode('utf-8')


elif platform.system().lower() == 'aix':
	pass


if platform.system().lower() == 'linux' and os.geteuid() != 0:
	print('please run used root')
elif platform.system().lower() == 'linux':
	ip()
	os_version()
	uptime()
	now_time()
	lv()
	message_log()
	dmesg_log()
	cpu()
	process()
	process_zombie()
	disk()
	mem_info()
	swap()
	data = json.dumps(result,ensure_ascii=False,indent=4)
	print(data)

elif platform.system().lower() == 'windows':
	ip()
	os_version()
	uptime()
	now_time()
	cpu()
	process()
	disk()
	memory()
	swap_mem()
	data = json.dumps(result,ensure_ascii=False,indent=4)
	print(data)


