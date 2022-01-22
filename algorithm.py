# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 14:39:36 2020

@author: lenovo
"""



import pandas as pd
import numpy as np
import re
import subprocess
import time
from os import popen
import random
import copy

cpus = 16

def get_container_list():  #get completed container
    command_name = ('docker ps --format "table {{.Names}}\t{{.Status}}"')
    container_table = subprocess.getoutput(command_name)
    container_status = container_table.splitlines()[1:]
    container_list = []
    for line in container_status:
        tmp_status = line.split()
#        print("tmp_status: ", tmp_status)
        if tmp_status[-1] == 'minutes' or tmp_status[-1] == 'minute': #  when the contaienr status is "Up About a minute" or "Up xx minutes"
            container_list.append(tmp_status[0])
        else:
            if int(tmp_status[2]) > 40 and len(tmp_status) <= 4:  #when status is bigger than 40 seconds and not the "less than a second"
                container_list.append(tmp_status[0])
#    print("function get_container_list: ", container_list)
    
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
#    print("function get_container_startline: ", start_count)
    return start_count

def get_batch_time(container_name):
    command_log = 'docker logs {}'.format(container_name)
    time_log = subprocess.getoutput(command_log)
    print("get batch time log: ", time_log)
    batch_time = time_log.splitlines()
    start_line = get_container_startline(container_name)
    batch_time = batch_time[start_line+1:]
#    print("function get_batch_time: ", batch_time)
    return batch_time

def get_cpu():
    command_cpu = ('docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}"')
    cpu_log = subprocess.getoutput(command_cpu)
    cpu_data =  cpu_log.splitlines()[1:]
    final_data = {}
    for i in cpu_data:
        temp_data = re.split('\s+', i)
        final_data[temp_data[0]] = float(temp_data[1][:-1])/(cpus*100)
#    print("function get cpu: ", final_data)
    return final_data


container_model_list = ["fuzzychen/1000batch","fuzzychen/vgg16","fuzzychen/inceptionv3","fuzzychen/res50","fuzzychen/xcep"]
#def run_container(container_name,container_model):
#    command_run = 'nohup docker run --name {} {} > {}.log &'.format(container_name,container_model,container_name)
#    subprocess.Popen(command_run,shell=True)
#    print("Succesfully run container ",container_name,"collecting data now!")

def number_regulate(x):
    if x > cpus:
        x = cpus
    elif x < 0.2:
        x = 0.2
    return round(x,2)



def performance_manage(container_num, container_list, resource, usage_history):
    G,B,D  = [],[],[]
    Qg,Qd = 0,0
    performance = []
    q = [0] * container_num
    adjust_list = []
    for i in range(container_num):
        Qg_ind,Qd_ind = 0,0
        cpu_data = get_cpu()
        current_cpu = cpu_data[container_list[i]]
        usage_history[container_list[i]].append(current_cpu)
        total_usg_record[container_list[i]].append(current_cpu)
#        print("total_usg_record: ", total_usg_record)
#        print("container_list[i]: ", container_list[i], i)
        
        current_performance = get_batch_time(container_list[i])[-1]

        if container_list[i] in history_batch_time:
            if current_performance != history_batch_time[container_list[i]]:
                history_batch_time[container_list[i]] = current_performance
                adjust_list.append(i)
        else:
            history_batch_time[container_list[i]] = current_performance
            adjust_list.append(i)

        current_performance = float(current_performance)
        performance.append(current_performance)
        q[i] = target[i] - current_performance

        if q[i] > target[i]*0.1:
            G.append(container_list[i])
            #Rg += resource[i]
            Qg += q[i]
            Qg_ind += q[i]
        elif q[i] < -target[i]*0.1:
            D.append(container_list[i])
            #Rd += resource[i]
            Qd += q[i]
            Qd_ind += q[i]
        else:
            B.append(container_list[i])
            
        indiv_performance[container_list[i]].append([Qg_ind, Qd_ind])
#        print("indiv_performance: ", indiv_performance)
        

    #setting update rate depends onn how many container left to adjust
#    print("The adjust adjust_rate_B is ",adjust_list)
    G_update_rate = len(G) * alpha
    D_update_rate = len(D) * alpha

    for i in adjust_list:
        if container_list[i] in G:
            resource[i] *= 1 - (q[i]/Qg)*G_update_rate
            resource[i] = number_regulate(resource[i])
        elif container_list[i] in D:
            resource[i] *= 1 + (q[i]/Qd)*D_update_rate
            resource[i] = number_regulate(resource[i])
        command_log = 'docker update --cpus {} {}'.format(resource[i],container_list[i])
        subprocess.Popen(command_log,shell=True)
    
    return adjust_list, G, D, B, q, resource, Qg, Qd



def adaptive_listener(adjust_list, container_list, G, D, B, q, iv_time, IV):
    Qb, Qw, Qs = 0,0,0
#    Qb_1, Qw_1, Qs_1 = 0, 0, 0
    
   # IV = 20
    beta = 2
    print("Alg2---------------------------")
    print("adjust_list: ", adjust_list)
    print("container_list: ", container_list)
    print("G: ", G)
    print("D: ", D)
    print("B: ", B)
    
    for i in adjust_list:
        if container_list[i] in G:
            Qb = Qb + q[i]
#            print("Qb: ", Qb)
        elif container_list[i] in D:
            Qw = Qw + q[i]
#            print("Qw: ", Qw)
        elif container_list[i] in B:
            Qs = len(B)
#            print("Qs: ", Qs)
    alg2_resource.append([Qb, Qw, Qs])


    if t >= 2 :
        if abs(alg2_resource[-1][0] - alg2_resource[-2][0]) < beta and abs(alg2_resource[-1][1] - alg2_resource[-2][1]) < beta:
#            iv_time += 1
#            if iv_time >= 3:
            IV = IV * 2 
#            iv_time = 0
        elif alg2_resource[-1][2] < alg2_resource[-2][2]:
            IV = IV / 2
        else:
            IV = IV
        print("IV: ", IV)
    if IV < 20:
        IV = 20

    return IV, alg2_resource


def without_alg(container_num, container_list, usage_history):
    G,B,D  = [],[],[]
    Qg,Qd = 0,0
    performance = []
    q = [0] * container_num
    adjust_list = []
    for i in range(container_num):
        Qg_ind,Qd_ind = 0,0
        cpu_data = get_cpu()
        current_cpu = cpu_data[container_list[i]]
        usage_history[container_list[i]].append(current_cpu)
        total_usg_record[container_list[i]].append(current_cpu)
#        print("total_usg_record: ", total_usg_record)
        print("container_list[i]: ", container_list[i], i)
        
        current_performance = get_batch_time(container_list[i])[-1]

        if container_list[i] in history_batch_time:
            if current_performance != history_batch_time[container_list[i]]:
                history_batch_time[container_list[i]] = current_performance
                adjust_list.append(i)
        else:
            history_batch_time[container_list[i]] = current_performance
            adjust_list.append(i)

        current_performance = float(current_performance)
        performance.append(current_performance)
        q[i] = target[i] - current_performance

        if q[i] > target[i]*0.1:
            G.append(container_list[i])
            #Rg += resource[i]
            Qg += q[i]
            Qg_ind += q[i]
        elif q[i] < -target[i]*0.1:
            D.append(container_list[i])
            #Rd += resource[i]
            Qd += q[i]
            Qd_ind += q[i]
        else:
            B.append(container_list[i])
    return adjust_list, G, D, B, q, Qg, Qd


#Initialize


resource_history = []
print('The default Limit is: ',resource_history)
performance_history = []
performance_history1 = []

alg2_resource = []
#target = [10+i for i in range(container_num)]
target = [20,20,20,20,20,20,20]
'''
target = []
for i in range(container_num):
    target.append(random.randint(15,40))
target.sort()
'''

print("The target time is: ",target)
IV_list = []

alpha = 0.2
IV = 20
total_time = 0
iv_time = 0
history_batch_time = {}

model_time = []
#container_numlist = []
old_containernum = 0
container_list_tmp = ["test1","test2","test3","test4","test5","test6","test7","test8","test9","test10"]
values = [[], [], [],[], [], [],[], [], [],[]]
total_usg_record = dict(zip(container_list_tmp, values))

container_list_tmp2 = ["test1","test2","test3","test4","test5","test6","test7","test8","test9","test10"]
values2 = [[], [], [],[], [], [],[], [], [],[]]
indiv_performance = dict(zip(container_list_tmp2, values2))
B = 0



for t in range(12):
    # G = too fast,  D = too slow, B = balanced
    start_time = time.time()
    print("start--------------", t, "times----")
    temp_cpu = get_cpu()
    container_list,container_num = get_container_list()
    print("The container list is: ",container_list)
    resource = [round(temp_cpu[i]*cpus,2) for i in container_list]
    usage_history = get_cpu()
    for i in usage_history:
        usage_history[i] = [usage_history[i]]
    print("resource: ", resource)
    print("usage_history: ", usage_history)
    
    
    
    if t > 2 and len(B) == container_num:
        adjust_list, G, D, B, q, Qg, Qd = without_alg(container_num, container_list, usage_history)
        IV, alg2_resource = adaptive_listener(adjust_list, container_list, G, D, B, q, iv_time, IV)
        print("skip the algorithm at: ", t, "times")
        IV_list.append(IV)
        time.sleep(IV)
        
        end_time = time.time()
        total_time += end_time - start_time
        model_time.append(end_time-start_time)
        print("The G at:",t,"Round still have",G)
        print("The D at:",t,"Round still have",D)
        print("The Limit at:",t,'Round', resource)
        performance_history.append([len(G),len(D)])
        performance_history1.append([Qg,Qd,total_time])
        update_resource = copy.deepcopy(resource)
        resource_history.append(update_resource)
        print(resource_history)
        
        if IV > 300 or total_time > 1200:
            print("stop reason: IV > 300 or total_time > 1200", IV > 300, total_time > 1200)
            break
        continue
    else:
        print("apply algorithm at: ", t, "times")
        # algorithm 1 
        adjust_list, G, D, B, q, resource, Qg, Qd = performance_manage(container_num, container_list, resource, usage_history)
        
        # algorithm 2
        IV, alg2_resource = adaptive_listener(adjust_list, container_list, G, D, B, q, iv_time, IV)



        
    print("alg2_resource: ", alg2_resource)
    IV_list.append(IV)
    time.sleep(IV)
    
    end_time = time.time()
    total_time += end_time - start_time

    model_time.append(end_time-start_time)
    
    
    
    print("The G at:",t,"Round still have",G)
    print("The D at:",t,"Round still have",D)
    print("The Limit at:",t,'Round', resource)
    performance_history.append([len(G),len(D)])
    performance_history1.append([Qg,Qd,total_time])
    update_resource = copy.deepcopy(resource)
    resource_history.append(update_resource)
    print(resource_history)
    print("The balanced container: ",B)
    print("performance_history1: ", performance_history1)
    print("IV_list: ", IV_list)
#    if t > 4:
#        if alg2_resource[-1][0] == 0 and alg2_resource[-1][1] == 0 and alg2_resource[-2][0] == 0 and alg2_resource[-2][1] == 0 and alg2_resource[-3][0] == 0 and alg2_resource[-3][1] == 0:
#            print("stop reason, three times equal to 0")
#            break
    if IV > 300 or total_time > 1200:
        print("stop reason: IV > 300 or total_time > 1200", IV > 300, total_time > 1200)
        break
    
np.savetxt('test.out', (1,1,1))
print("end--------------------------")

print("total performance_history1: ", performance_history1)
print("total resource_record: ", resource_history)
print("total usage_history: ", total_usg_record)
print("indiv_performance", indiv_performance)
print("IV_list: ", IV_list)

performance_history = np.array(performance_history)
performance_record = pd.DataFrame({'G': performance_history[:,0], 'D': performance_history[:, 1]})
performance_history1 = np.array(performance_history1)
performance_record1 = pd.DataFrame({'G': performance_history1[:,0], 'D': performance_history1[:, 1], 'Runing_Time': performance_history1[:, 2]})
#resource_history = np.array(resource_history)
#resource_record = pd.DataFrame(resource_history,columns = container_list)


def cal_average(num):
    sum_num = 0
    for t in num:
        sum_num = sum_num + t           

    avg = sum_num / len(num)
    return avg

print(" the model time is :", cal_average(model_time))


performance_record.to_csv("p.csv")
performance_record1.to_csv("p1.csv")
# usg_record = pd.DataFrame.from_dict(total_usg_record)
# usg_record.to_csv("u.csv")
#resource_record.to_csv("r.csv")