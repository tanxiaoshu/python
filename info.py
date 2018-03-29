#/usr/bin/env python
#coding:utf-8
#author:TanXiaoshu
#date:2018.3.27

from multiprocessing import cpu_count
import subprocess
import time
import platform
from collections import OrderedDict
import re
import socket
import json
import sys


# minions = {'cpu_percent':50,'mem_percent':50,'disk_percent':50,'load1':10,'load5':10,'load15':10}

minions = eval(sys.argv[1])
version = platform.python_version().split('.')[0]
server_information = {}
information = {}
disk = {}

def cpu_info():
    if platform.system() == "Linux":
        information['cpu_core'] = cpu_count()
        cmd1 = subprocess.Popen('cat /proc/stat|grep -w cpu',shell=True,stdout=subprocess.PIPE)
        cpu_info1 = cmd1.stdout.read().strip().split()
        cpu_used1 = int(cpu_info1[1])
        total1 = int(cpu_info1[1])+int(cpu_info1[2])+int(cpu_info1[3])+int(cpu_info1[4])+int(cpu_info1[5])+int(cpu_info1[6])+int(cpu_info1[7])
        time.sleep(1)
        cmd2 = subprocess.Popen('cat /proc/stat|grep -w cpu',shell=True,stdout=subprocess.PIPE)
        cpu_info2 = cmd2.stdout.read().strip().split()
        cpu_used2 = int(cpu_info2[1])
        total2 = int(cpu_info2[1])+int(cpu_info2[2])+int(cpu_info2[3])+int(cpu_info2[4])+int(cpu_info2[5])+int(cpu_info2[6])+int(cpu_info2[7])
        cpu_idel = cpu_used2 - cpu_used1
        total = total2 - total1
        cpu_used = cpu_idel*100//total
        #cpu_information['cpu_used'] = cpu_used

        if cpu_used > minions['cpu_percent']:
            information['cpu_status'] = "异常"
        else:
            information['cpu_status'] = "正常"
        return {'cpu_percent': information['cpu_status'], 'cpu_count': information['cpu_core']}
    elif platform.system() == "Windows":
        return {'cpu_percent': None, 'cpu_count': None}

def mem_info():
    if platform.system() == "Linux":
        meminfo = OrderedDict()
        with open('/proc/meminfo') as f:
            for line in f:
                meminfo[line.split(':')[0]] = int(line.split(':')[1].strip().split()[0])
        information['total_mem'] = meminfo['MemTotal']
        #mem_information['free_mem'] = meminfo['MemFree']
        used_mem = int(meminfo['MemTotal']) - int(meminfo['MemFree']) - int(meminfo['Buffers']) - int(meminfo['Cached'])
        information['used_mem'] = str((int(meminfo['MemTotal']) - int(meminfo['MemFree']) - int(meminfo['Buffers']) - int(meminfo['Cached']))//1024) + "M"
        #print(mem_information)
        mem_used_percent = int(used_mem)*100//int(meminfo['MemTotal'])
        #print(mem_used_percent)
        if mem_used_percent > minions['mem_percent']:
            information['mem_status'] = '异常'
        else:
            information['mem_status'] = '正常'
        return {'mem_total':information['total_mem'],'mem_percent':information['mem_status']}
    elif platform.system() == "Windows":
        return {'mem_total':None, 'mem_percent': None}

def disk_info():
    if platform.system() == "Linux":
        cmd = subprocess.Popen('df -h',shell=True,stdout=subprocess.PIPE)
        if version == "2":
            stdout = cmd.stdout.read().strip().split('\n')
        elif version == "3":
            stdout = cmd.stdout.read().decode().strip().split('\n')
        for line in stdout:
            if re.match("/dev/",line):
                line = line.split()
                disk_detail = {}
                #disk['total'] = line[1]
                #disk['free'] = line[3]
                disk_detail['used_percent'] = line[4]
                if int(line[4].split("%")[0]) > minions['disk_percent']:
                    disk_detail['disk_status'] = "异常"
                else:
                    disk_detail['disk_status'] = "正常"
                disk[line[5]] = disk_detail
                json.dumps(disk,ensure_ascii=False)
        information['disk_info'] = disk
        return information['disk_info']
    elif platform.system() == "Windows":
        return None

def hostname():
    if platform.system() == "Linux":
        cmd = subprocess.Popen('uname -n',shell=True,stdout=subprocess.PIPE)
        if version == "2":
            information['hostname'] = cmd.stdout.read().strip()
        elif version == "3":
            information['hostname'] = cmd.stdout.read().strip().decode()
        #print(information['hostname'])
        return information['hostname']
    elif platform.system() == "Windows":
        return None

def ip():
    if platform.system() == "Linux":
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except:
            ip = None
            s.close()
        information['ip'] = ip
        #print(information['ip'])
        return information['ip']

    elif platform.system() == "Windows":
        return None

def uptime():
    if platform.system() == "Linux":
        with open("/proc/uptime") as f:
            for line in f:
                information['sys_uptime'] = str(int(line.split()[0].split(".")[0])//86400) + "day"
                #print(information['sys_uptime'])
                return information['sys_uptime']

    elif platform.system() == "Windows":
        return None

def times():
    if platform.system() == "Linux":
        information['current_times'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        #print(information['times'])
        return information['current_times']
    elif platform.system() == "Windows":
        return None

def load():
    if platform.system() == "Linux":
        with open('/proc/loadavg') as f:
            con = f.read().split()
            # information['load1'] = con[0]
            # information['load5'] = con[1]
            # information['load15'] = con[2]
            if float(con[0]) >minions['load1']:
                information['load1'] = "异常"
            else:
                information['load1'] = "正常"

            if float(con[1]) >minions['load5']:
                information['load5'] = "异常"
            else:
                information['load5'] = "正常"

            if float(con[2]) >minions['load15']:
                information['load15'] = "异常"
            else:
                information['load15'] = "正常"
        return {'load1':information['load1'],'load5':information['load5'],'load15':information['load15']}

    elif platform.system() == "Windows":
        return {'load1':None,'load5':None,'load15':None}

def tcp_link():
    if platform.system() == "Linux":
        link_num = subprocess.Popen('netstat -na|grep ESTABLISHED|wc -l',shell=True,stdout=subprocess.PIPE)
        information['tcp_link'] = int(link_num.stdout.read().strip())
        return information['tcp_link']
    elif platform.system() == "Windows":
        return None

cpuinfo = cpu_info()
meminfo = mem_info()

result = {
    'cpu_percent':cpuinfo['cpu_percent'],
    'cpu_count':cpuinfo['cpu_count'],
    'mem_total':meminfo['mem_total'],
    'mem_percent':meminfo['mem_percent'],
    'diskinfo':json.dumps(disk_info(),ensure_ascii=False),
    'hostname':hostname(),
    'ip':ip(),
    'uptime':uptime(),
    'nowtime':times(),
    'tcpcount':tcp_link(),
}
result.update(load())

print(json.dumps(result,ensure_ascii=False))
