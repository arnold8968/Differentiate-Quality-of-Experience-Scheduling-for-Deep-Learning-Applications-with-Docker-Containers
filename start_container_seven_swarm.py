import re
import subprocess
import time
from os import popen
import random

#Clear all history


command_stop = "docker service ls -q | xargs docker service rm"
subprocess.Popen(command_stop,shell=True)
time.sleep(5)

def run_container(container_name,container_model):
    command_run =  "nohup docker service create -d --restart-condition none --name {} {} > {}.log &". format(container_name,container_model,container_name)
    subprocess.Popen(command_run,shell=True)
    print("Succesfully run container ",container_name,"collecting data now!")

container_list = ["test1","test2","test3","test4","test5","test6","test7"]
container_model_list = ["fuzzychen/1000batch","fuzzychen/vgg16","fuzzychen/inceptionv3","fuzzychen/res50","fuzzychen/xcep"]
ran_list = random.sample(range(len(container_model_list)), len(container_model_list))
print(ram_list)

for i in range(1, 28):
    run_container('test{}'.format(i), container_model_list[ran_list[i % len(container_model_list)]])
    print('test{}'.format(i), container_model_list[ran_list[i % len(container_model_list)]])
    print("initializing~~~~~~~~~~~~Takes 180 seconds")
    time.sleep(3)

time.sleep(120)