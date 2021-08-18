#!/usr/bin/env python3 

from hpcg import Hpcg

hpcg = Hpcg(
    prefix = '../run/HPCG',
    sif    = '../images/hpc-benchmarks_20.10-hpcg.sif')

hpcg.run() 
hpcg.summary()
