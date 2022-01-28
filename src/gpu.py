#!/usr/bin/env python3 

import os
import logging
import re

from utils import syscmd

def nvidia_smi(host):
    gpu        = {} 

    try: 
        nvidia_smi = syscmd(f'ssh -oStrictHostKeyChecking=no {host} "nvidia-smi -L"')

        for line in nvidia_smi.splitlines():
            gpu_id, gpu_name, gpu_uuid = re.search('^GPU (\d+): \w+ (.+?) \(UUID: (.+?)\)', line).groups()
            gpu[gpu_id] = [gpu_name, gpu_uuid] 
    except: 
        pass

    return gpu

def gpu_info(gpu):
    for index in gpu: 
        logging.info(f'{"GPU "+index:7} : {gpu[index][0]} {gpu[index][1]}')

def gpu_memory(host): 
    memory = syscmd(f'ssh -oStrictHostKeyChecking=no {host} "nvidia-smi -i 0 --query-gpu=memory.total --format=csv,noheader"').split()[0]

    return int(memory)

def gpu_affinity(host):
    affinity = [] 
    topology = syscmd(f'ssh -oStrictHostKeyChecking=no {host} "nvidia-smi topo -m"')

    for line in topology.splitlines():
        if re.search('^GPU\d+', line): 
            numa = line.split()[-1]
            if re.search('^\d+$', numa): 
                affinity.append(numa) 
            else: 
                affinity.append('0') 

    return affinity

def device_query(host): 
    homedir = os.environ['HOME']

    syscmd(f'wget https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Samples/deviceQuery/deviceQuery.cpp -O {homedir}/deviceQuery.cpp')
    syscmd(f'wget https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Common/helper_cuda.h -O {homedir}/helper_cuda.h')
    syscmd(f'wget https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Common/helper_string.h -O {homedir}/helper_string.h')
    syscmd(f'builtin cd; nvcc -I. deviceQuery.cpp -o deviceQuery')

    query = syscmd(f'ssh -oStrictHostKeyChecking=no {host} ./deviceQuery')

    for line in query.splitlines():
        if re.search('\/ Runtime Version', line): 
            runtime = line.split()[-1]

        if re.search('Minor version number', line): 
            cuda_cc = line.split()[-1].replace('.', '')
            break

    # clean up 
    [os.remove(f'{homedir}/{file}') for file in ['deviceQuery.cpp', 'helper_cuda.h', 'helper_string.h', 'deviceQuery']]

    return runtime, cuda_cc
