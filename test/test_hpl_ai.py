#!/usr/bin/env python3 

from hpl import Hpl

hpl = Hpl(
    prefix    = '../run/HPL',
    sif       = '/home/moasys/BMT/images/hpc-benchmarks:21.4-hpl.sif',
    blocksize = [1024], 
    ai        = True )

hpl.run() 
hpl.summary() 
