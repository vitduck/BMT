#!/usr/bin/env python3

cmd = { 
    'nvidia'      : 'ssh nvidia-smi', 
    'connectx'    : 'ssh /usr/sbin/lspci',
    'hpc_sdk'     : 'nvfortran --version', 
    'gcc'         : 'gcc --version', 
    'pgi'         : 'pgcc --version', 
    'cuda'        : 'nvcc --version', 
    'openmpi'     : 'mpirun --version',
    'singularity' : 'singularity --version', 
    'cmake'       : 'cmake --version' }

regex = { 
    'nvidia'      : 'Version:\s*([\d.]+)', 
    'connectx'    : 'ConnectX\-(\d)', 
    'hpc_sdk'     : 'nvfortran\s*([\d.]+)',
    'gcc'         : '\(GCC\)\s*([\d.]+)', 
    'pgi'         : 'pgcc\s*([\d.]+)', 
    'cuda'        : 'release\s*([\d.]+)',
    'openmpi'     : 'mpirun.+?([\d.]+)', 
    'singularity' : 'singularity.+?([\d.]+)', 
    'cmake'       : 'cmake version\s*([\d.]+)' } 
