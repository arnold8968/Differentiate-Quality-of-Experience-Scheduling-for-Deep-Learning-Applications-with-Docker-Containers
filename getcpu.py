import pandas as pd
import numpy as np
import re
import subprocess
import time
from os import popen
import random
import copy

cpus = 16

def get_cpu():
    command_cpu = ('docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}"')
    cpu_log = subprocess.getoutput(command_cpu)
    cpu_data =  cpu_log.splitlines()[1:]
    final_data = {}
    for i in cpu_data:
        temp_data = re.split('\s+', i)
        final_data[temp_data[0]] = float(temp_data[1][:-1])/(cpus*100)
    # print("function get cpu: ", final_data)
    return final_data


# from subprocess import DEVNULL
# subprocess.Popen('docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}" | ts %.s  >> docker_stats.log',shell=True,stdout=DEVNULL)
def get_batch_time(container_name):
    command_log = 'docker logs {}'.format(container_name)
    time_log = subprocess.getoutput(command_log)
    print("get batch time log: ", time_log)
    batch_time = time_log.splitlines()
    start_line = get_container_startline(container_name)
    batch_time = batch_time[start_line+1:]
#    print("function get_batch_time: ", batch_time)
    return batch_time

def get_container_list():  #get completed container
    command_name = ('docker ps --format "table {{.Names}}\t{{.Status}}"')
    container_table = subprocess.getoutput(command_name)
    container_status = container_table.splitlines()[1:]
    container_list = []
    for line in container_status:
        tmp_status = line.split()
        print("tmp_status: ", tmp_status)
        if tmp_status[-1] == 'minutes' or tmp_status[-1] == 'minute': #  when the contaienr status is "Up About a minute" or "Up xx minutes"
            container_list.append(tmp_status[0])
        else:
            if int(tmp_status[2]) > 50 and len(tmp_status) <= 4:  #when status is bigger than 40 seconds and not the "less than a second"
                container_list.append(tmp_status[0])
    print("function get_container_list: ", container_list)
    
    return container_list, len(container_list)

def get_container_startline(container_name):
    command_log = 'docker logs {}'.format(container_name)
    time_log = subprocess.getoutput(command_log)
    batch_log = time_log.splitlines()
    start_count = 0
    for i in batch_log:
        if "0us/step" in i:
            break
        start_count += 1
    print("function get_container_startline: ", start_count)
    return start_count

import os
flag = os.path.isfile('test.out')

start_time = time.time()
cpu_list = []
time_dic = {'runningtime':[]}
performance_dic = {}
while flag == False: 
    # print(get_cpu())
    current_time = time.time()
    time_dic['runningtime'].append(current_time-start_time)
    cpu_list.append(get_cpu())
    container_list,container_num = get_container_list()
    df_cpu = pd.DataFrame(cpu_list)
    df_runningtime = pd.DataFrame(time_dic)
    df_cpu['runningtime'] = df_runningtime
    print(df_cpu)

    for i in range (len(container_list)):
    # for i in range(container_num):
        # current_performance = {container_list[i]:get_batch_time(container_list[i])[-1]}
        print(i)
        print(container_list[i])
        print(get_batch_time(container_list[i]))
        print(get_batch_time(container_list[i])[-1])
        current_performance = get_batch_time(container_list[i])[-1]
        # print('performance:',current_performance)
        performance_dic.setdefault(container_list[i], []).append(current_performance)
        # performance_dic[container_list[i]]=current_performance
    print('performance:',performance_dic)
    # df_per = pd.DataFrame(performance_dic,index=[0])
    df_per = pd.DataFrame.from_dict(performance_dic,orient='index').T
    print(df_per)
    flag = os.path.isfile('test.out')
    	
    time.sleep(10)
    if flag == True:
        break
    
# df_cpu = pd.DataFrame(cpu_list)
# print(df_cpu)
df_cpu.to_csv("cpu.csv")
# df_per.to_csv("performance.csv")