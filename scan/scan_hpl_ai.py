#!/usr/bin/env python3 

from hpl import Hpl_Ai

hpl = Hpl_Ai(
    prefix    = '../run/HPL',
    sif       = '../image/hpc-benchmarks:21.4-hpl.sif',
    blocksize = [1024] ) 

hpl.info()

for nodes in [1]:
    for ngpus in [2, 4, 6, 8]:
        for omp in [1, 2, 4, 8]: 
            hpl.nodes = nodes
            hpl.ngpus = ngpus
            hpl.omp   = omp
        
            hpl.matrix_size() 
            hpl.run() 

hpl.summary()
