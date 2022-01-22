# Differentiate-Quality-of-Experience-Scheduling-for-Deep-Learning-Applications-with-Docker-Containers

## Installation Requirements
Python version: 3.70
Docker Swarm version: 18.06.2

Docker Swarm install 

Step 1 install docker in all nodes. chmod 777 install.sh ./install.sh

Step 2 In master node init docker swarm by using: docker swarm init

The output contains the: docker swarm join-token command

Step 3 Copy swarm token command and paste in each workers, which let the worker join in the Swarm

check the state -- docker node ls -- docker service ls

update git` git pull origin master

## Scripts Instruction

install.sh (Install docker)
start_container_seven.py (start seven containers at the same time)
competition.py (without any algorithm)
algorithm.py (algorithm script)


