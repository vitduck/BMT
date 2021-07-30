#!/usr/bin/env python3 

import os 

from hpl import Hpl

hpl = Hpl(
    prefix = '../run/HPL',
    sif    = '../images/hpc-benchmarks_20.10-hpl.sif' )

#  hpl.debug() 

hpl.make_outdir() 
hpl.write_hostfile() 
hpl.write_input() 
hpl.run() 
