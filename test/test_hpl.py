#!/usr/bin/env python3 

from hpl import Hpl

hpl = Hpl(
    prefix = '../run/HPL',
    sif    = '../image/hpc-benchmarks:21.4-hpl.sif' )

hpl.info()
hpl.run() 
hpl.summary() 
