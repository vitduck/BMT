#!/usr/bin/env python3 

import os
import re

from utils import syscmd

def gpu_id(host):
    nvidia_smi = syscmd(f'ssh {host} "nvidia-smi -L"')

    gpu = re.findall('GPU\s+(\d+)', nvidia_smi)

    return [i for i in gpu]

def gpu_info(host):
    print('> GPU')
    nvidia_smi = syscmd(f'ssh {host} "nvidia-smi -L"')
    
    for gpu in nvidia_smi.splitlines():
        print(' '.join(gpu.split()[0:4]))
    
    print()

def gpu_memory(host): 
    memory = syscmd(f'ssh {host} "nvidia-smi -i 0 --query-gpu=memory.total --format=csv,noheader"').split()[0]

    return int(memory)

def gpu_affinity(host):
    affinity = [] 
    topology = syscmd(f'ssh {host} "nvidia-smi topo -m"')

    for line in topology.splitlines():
        if re.search('^GPU\d+', line): 
            affinity.append(line.split()[-1])

    return affinity

def device_query(host): 
    homedir = os.environ['HOME']

    syscmd(f'wget https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Samples/deviceQuery/deviceQuery.cpp -O {homedir}/deviceQuery.cpp')
    syscmd(f'wget https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Common/helper_cuda.h -O {homedir}/helper_cuda.h')
    syscmd(f'wget https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Common/helper_string.h -O {homedir}/helper_string.h')
    syscmd(f'builtin cd; nvcc -I. deviceQuery.cpp -o deviceQuery')

    query = syscmd(f'ssh {host} ./deviceQuery')

    for line in query.splitlines():
        if re.search('\/ Runtime Version', line): 
            runtime = line.split()[-1]

        if re.search('Minor version number', line): 
            cuda_cc = line.split()[-1].replace('.', '')
            break

    # clean up 
    [os.remove(f'{homedir}/{file}') for file in ['deviceQuery.cpp', 'helper_cuda.h', 'helper_string.h', 'deviceQuery']]

    return runtime, cuda_cc
