#!/usr/bin/env python3 

from hpcg import Hpcg

hpcg = Hpcg(
    prefix = '../run/HPCG',
    sif    = '../image/hpc-benchmarks_20.10-hpcg.sif')

for nodes in [1, 2]:
    for omp in [1, 2, 4]: 
        for grid in [64, 128, 256]: 
            hpcg.nodes = nodes
            hpcg.omp   = omp
            hpcg.grid  = [grid, grid, grid]
        
            hpcg.run() 

# hpcg.summary()
hpcg.summary(sort=1, order='>')
