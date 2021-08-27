#!/usr/bin/env python3 

from hpcg import Hpcg

hpcg = Hpcg(
    prefix = '../run/HPCG',
    sif    = '../images/hpc-benchmarks_20.10-hpcg.sif')

for nodes in [1, 2]:
    for grid in [64, 128, 256]: 
        for ngpus in [2]: 
            for omp in [1, 2, 4]: 
                hpcg.nodes = nodes
                hpcg.grid  = [grid, grid, grid]
                hpcg.ngpus = ngpus
                hpcg.omp   = omp
        
                hpcg.run() 

hpcg.summary()
