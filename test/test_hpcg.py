#!/usr/bin/env python3 

from hpcg import Hpcg

hpcg = Hpcg(
    prefix = '../run/HPCG',
    sif    = '../image/hpc-benchmarks:21.4-hpcg.sif' )

hpcg.run() 
hpcg.summary()
