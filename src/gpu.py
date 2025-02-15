#!/usr/bin/env python3 

import os
import logging
import re

from env   import get_module
from utils import syscmd

def nvidia_smi(): 
    device = {} 

    nvidia_smi = syscmd(['nvidia-smi -L'])

    for line in nvidia_smi.splitlines():
        id, name, uuid = re.search('^GPU (\d+): (.+?) \(UUID: (.+?)\)', line).groups()
        device[id] = [name, uuid] 

    return device

def gpu_memory():
    memory = syscmd([[
        'nvidia-smi', 
            '-i 0',  
            '--query-gpu=memory.total', 
            '--format=csv,noheader']]).split()[0]

    return int(memory)

def gpu_affinity(): 
    affinity = [] 
    topology = syscmd(['nvidia-smi topo -m'])

    for line in topology.splitlines():
        if re.search('^GPU\d+', line): 
            numa = line.split()[-1]
            
            affinity.append(numa) 

    return affinity

def gpu_info(device):
    for index in device: 
        logging.info(f'{"GPU "+index:7} : {device[index][0]} {device[index][1]}')

def device_query(builddir='./'): 
    # requirement to build deviceQuery
    sample_url = [ 
        'https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Common/helper_cuda.h',  
        'https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Common/helper_string.h', 
        'https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Samples/1_Utilities/deviceQuery/deviceQuery.cpp' ]
    
    # download cuda samples 
    for url in sample_url:
        file_name = url.split('/')[-1]
        file_path = os.path.join(builddir, file_name)
        
        if not os.path.exists(file_path):
            syscmd([['wget', url, f'-O {file_path}']])
    
    # build deviceQuerry 
    syscmd([
       f'builtin cd {builddir}',
        'nvcc -I. deviceQuery.cpp -o deviceQuery'])

    # execute deviceQuerry in remote host 
    query = syscmd([f'cd {builddir}', './deviceQuery']) 
    
    for line in query.splitlines():
        if re.search('\/ Runtime Version', line): 
            runtime = line.split()[-1]

        if re.search('Minor version number', line): 
            cuda_cc = line.split()[-1].replace('.', '')
            break

    return runtime, cuda_cc
