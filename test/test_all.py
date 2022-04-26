#!/usr/bin/env python3 

import sys
import subprocess 

from utils import syscmd
from env   import module_load, module_unload

bmt  = { 
    'stream/omp' : { 
        'env' : [ 'gcc/4.8.5' ],  
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
    'qe/ngc' : { 
        'env' : [ 'gcc/8.3.0', 'cuda/11.4', 'cudampi/openmpi-4.1.1', 'singularity/3.9.7' ], 
        'cmd' : './test_qe_ngc.py' }, 
    'gromacs/ngc' : { 
        'env' : [ 'singularity/3.9.7' ], 
        'cmd' : './test_gromacs_ngc.py' }, 
    'hpl' : { 
        'env' : [ 'gcc/8.3.0', 'cuda/11.4', 'cudampi/openmpi-4.1.1', 'singularity/3.9.7'], 
        'cmd' : './test_hpl.py' }, 
    'hpl-ai':  { 
        'env' : [ 'gcc/8.3.0', 'cuda/11.4', 'cudampi/openmpi-4.1.1', 'singularity/3.9.7'], 
        'cmd' : './test_hpl_ai.py' }, 
    'hpcg' : { 
        'env' : [ 'gcc/8.3.0', 'cuda/11.4', 'cudampi/openmpi-4.1.1', 'singularity/3.9.7'], 
        'cmd' : './test_hpcg.py' }, 
    } 

for test in bmt:
    module_load(bmt[test]['env'])
    
    print(syscmd(bmt[test]['cmd']))

    module_unload(bmt[test]['env'])
