#!/usr/bin/env python3 

from hpl import Hpl

hpl = Hpl(
    prefix    = '../run/HPL',
    sif       = '../images/hpc-benchmarks_20.10-hpl.sif', 
    blocksize = [64, 128, 256])

for nodes in [1, 2]:
    for ngpus in [2]: 
        for omp in [1, 2, 4]: 
            hpl.nodes = nodes
            hpl.ngpus = ngpus 
            hpl.omp   = omp 
            
            hpl.matrix_size() 
            hpl.run() 

hpl.summary()
