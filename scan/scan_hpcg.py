#!/usr/bin/env python3 

from hpcg import Hpcg

hpcg = Hpcg(
    prefix = '../run/HPCG',
    sif    = '../image/hpc-benchmarks_20.10-hpcg.sif' )

hpcg.info() 

for nodes in [1]:
    for ngpus in [1, 2, 4, 6, 8]:
        for omp in [1, 2, 6, 4]: 
            for grid in [64, 128, 256]: 
                hpcg.nodes = nodes
                hpcg.omp   = omp
                hpcg.grid  = [grid, grid, grid]
        
                hpcg.run() 

hpcg.summary()
