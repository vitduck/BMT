#!/usr/bin/env python3 

import os 

from hpcg import Hpcg

hpcg = Hpcg(
    prefix = '../run/HPCG',
    sif    = '../images/hpc-benchmarks_20.10-hpcg.sif' )

hpcg.make_outdir() 
hpcg.write_hostfile() 
hpcg.write_input()
hpcg.run() 
