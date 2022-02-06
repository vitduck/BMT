#!/usr/bin/env python3 

import os
import logging
import re

from ssh   import ssh_cmd 
from utils import syscmd

def nvidia_smi(node):
    device = {} 

    nvidia_smi = syscmd(f'{ssh_cmd} {node} "nvidia-smi -L"')

    for line in nvidia_smi.splitlines():
        id, name, uuid = re.search('^GPU (\d+): (.+?) \(UUID: (.+?)\)', line).groups()
        device[id] = [name, uuid] 

    return device

def gpu_info(device):
    for index in device: 
        logging.info(f'{"GPU "+index:7} : {device[index][0]} {device[index][1]}')

def gpu_memory(node): 
    memory = syscmd(f'{ssh_cmd} {node} "nvidia-smi -i 0 --query-gpu=memory.total --format=csv,noheader"').split()[0]

    return int(memory)

def gpu_affinity(node):
    affinity = [] 
    topology = syscmd(f'{ssh_cmd} {node} "nvidia-smi topo -m"')

    for line in topology.splitlines():
        if re.search('^GPU\d+', line): 
            numa = line.split()[-1]
            if re.search('^\d+$', numa): 
                affinity.append(numa) 
            else: 
                affinity.append('0') 

    return affinity

def device_query(node): 
    homedir = os.environ['HOME']

    syscmd(f'wget https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Common/helper_cuda.h -O {homedir}/helper_cuda.h')
    syscmd(f'wget https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Common/helper_string.h -O {homedir}/helper_string.h')
    syscmd(f'wget https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Samples/1_Utilities/deviceQuery/deviceQuery.cpp -O {homedir}/deviceQuery.cpp')
    syscmd(f'builtin cd; nvcc -I. deviceQuery.cpp -o deviceQuery')

    query = syscmd(f'{ssh_cmd} {node} ./deviceQuery')

    for line in query.splitlines():
        if re.search('\/ Runtime Version', line): 
            runtime = line.split()[-1]

        if re.search('Minor version number', line): 
            cuda_cc = line.split()[-1].replace('.', '')
            break

    # clean up 
    for file in ['deviceQuery.cpp', 'helper_cuda.h', 'helper_string.h', 'deviceQuery']:
        os.remove(f'{homedir}/{file}')

    return runtime, cuda_cc
