#!/usr/bin/env python3 

import subprocess 
import sys

from utils import syscmd
from env   import module_load, module_unload

test = [] 

bmt  = { 
        'stream/omp' : { 
            'env' : [],  
            'cmd' : './test_stream_omp.py' }, 
        'stream/omp/intel' : { 
            'env' : [ 'intel/18.0.2' ], 
            'cmd' : './test_stream_omp.py' }, 
        'stream/cuda' : { 
            'env' : [ 'cuda/10.1' ], 
            'cmd' : './test_stream_cuda.py' }, 
        'iozone' : { 
            'env' : [], 
            'cmd' : './test_iozone.py' }, 
        'ior' : { 
            'env' : [ 'gcc/8.3.0', 'mpi/openmpi-3.1.5' ],  
            'cmd' : './test_ior.py' }, 
        'qe' : { 
            'env' : [ 'nvidia_hpc_sdk/21.5' ],  
            'cmd' : './test_qe.py' }, 
        'qe/ngc' : { 
            'env' : [ 'gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-4.0.5', 'singularity/3.6.4' ], 
            'cmd' : './test_qe_ngc.py' }, 
        'gromacs' : { 
            'env' : [ 'gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-4.0.5' ], 
            'cmd' : './test_gromacs.py' }, 
        'gromacs/ngc' : { 
            'env' : [], 
            'cmd' : './test_gromacs_ngc.py' }, 
        'gromacs/gpudirect/ngc' : { 
            'env' : [], 
            'cmd' : './test_gromacs_ngc.py --gpudirect' }, 
        'hpl' : { 
            'env' : [ 'gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-4.0.5', 'singularity/3.6.4'], 
            'cmd' : './test_hpl.py' }, 
        'hpl-ai':  { 
            'env' : [ 'gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-4.0.5', 'singularity/3.6.4'], 
            'cmd' : './test_hpl_ai.py' }, 
        'hpcg' : { 
            'env' : [ 'gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-4.0.5', 'singularity/3.6.4'], 
            'cmd' : './test_hpcg.py' }, 
    } 

if len(sys.argv) == 1 : 
    test = list(bmt.keys())
else: 
    test = sys.argv[1:len(sys.argv)]

for case in test:
    if  case in bmt: 
        module_load(bmt[case]['env'])
    
        print(syscmd(bmt[case]['cmd']))

        module_unload(bmt[case]['env'])
