#!/usr/bin/env python3 

from hpl_ai import Hpl_Ai

hpl = Hpl_Ai(
    prefix    = '../run/HPL',
    sif       = '../image/hpc-benchmarks:21.4-hpl.sif',
    blocksize = [1024] )

hpl.info()
hpl.run() 
hpl.summary() 
