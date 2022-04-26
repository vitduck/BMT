#!/usr/bin/env python3

from ior     import Ior
from openmpi import OpenMPI

ior = Ior(
    prefix = '../run/IOR', 
    mpi   = OpenMPI( 
        task = 8 ))

ior.info()
ior.download() 
ior.build()
ior.run() 
ior.summary()
