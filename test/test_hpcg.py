#!/usr/bin/env python3 

from hpcg import Hpcg

hpcg = Hpcg(
    prefix = '../run/HPCG',
    sif    = '../image/hpc-benchmarks_20.10-hpcg.sif')

#hpcg.debug()
hpcg.run() 
hpcg.summary()
#hpl.summary(sort=1, order='>')
