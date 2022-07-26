#!/usr/bin/env python3 

import sys
import subprocess 

from utils import syscmd
from env import module_load, module_unload

n = 3

bmt = { 
    'stream/omp' : { 
        'env' : ['gcc/4.8.5'],
        'cmd' : [f'./test_stream_omp.py --repeat {n}']}, 

    'stream/omp/intel' : { 
        'env' : ['intel/18.0.2'],
        'cmd' : [f'./test_stream_omp.py --repeat {n}']}, 

    'stream/cuda' : { 
        'env' : ['cuda/10.1'],
        'cmd' : [f'./test_stream_cuda.py --repeat {n}']}, 

    'iozone' : { 
        'env' : [],
        'cmd' : [f'./test_iozone.py --repeat {n}']}, 

    'ior' : { 
        'env' : ['gcc/8.3.0', 'mpi/openmpi-3.1.5'],
        'cmd' : [f'./test_ior.py --repeat {n}']}, 

    'qe' : { 
        'env' : ['gcc/8.3.0', 'nvidia_hpc_sdk/21.5'],
        'cmd' : [f'./test_qe_gpu.py --repeat {n}']}, 

    'qe/ngc' : { 
        'env' : ['gcc/8.3.0', 'cuda/11.4', 'cudampi/openmpi-4.1.1', 'singularity/3.9.7'], 
        'cmd' : [f'./test_qe_gpu.py --sif ../image/qe-6.8.sif --repeat {n}']}, 

    'gromacs' : { 
        'env' : ['gcc/8.3.0', 'cuda/11.4' ], 
        'cmd' : [f'./test_gromacs_gpu.py --repeat {n}']},

    'gromacs/ngc' : { 
        'env' : ['singularity/3.9.7' ], 
        'cmd' : [f'./test_gromacs_gpu.py --sif ../image/gromacs-2021.3.sif --repeat {n}']},

    'hpl' : { 
        'env' : ['gcc/8.3.0', 'cuda/11.4', 'cudampi/openmpi-4.1.1', 'singularity/3.9.7'],
        'cmd' : [f'./test_hpl_gpu.py --repeat {n}'] }, 

    'hpl-ai':  { 
        'env' : ['gcc/8.3.0', 'cuda/11.4', 'cudampi/openmpi-4.1.1', 'singularity/3.9.7'], 
        'cmd' : [f'./test_hpl_ai_gpu.py --repeat {n}'] }, 

    'hpcg' : { 
        'env' : ['gcc/8.3.0', 'cuda/11.4', 'cudampi/openmpi-4.1.1', 'singularity/3.9.7'], 
        'cmd' : [f'./test_hpcg_gpu.py --repeat {n}'] }, 
    } 

for test in bmt:
    module_load(bmt[test]['env'])
    
    print(syscmd(bmt[test]['cmd']))

    module_unload(bmt[test]['env'])
