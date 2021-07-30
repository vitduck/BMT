#!/usr/bin/env python3 

from hpc_nvidia import HpcNvidia

hpc = HpcNvidia(
    prefix         = './',
    gpu            = [0, 1], 
    gpu_per_socket = [0, 2], 
    thread         = 4, 
    sif            = '../images/hpc-benchmarks_20.10-hpl.sif' )

hpc.debug() 
# hpc.run()
