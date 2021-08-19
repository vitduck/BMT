#!/usr/bin/env python3 

from hpl import Hpl

hpl = Hpl(
    prefix = '../run/HPL',
    sif    = '../images/hpc-benchmarks_20.10-hpl.sif')

hpl.run() 
hpl.summary() 
#  hpl.summary(sort=1, order='>')
