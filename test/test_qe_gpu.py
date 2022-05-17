#!/usr/bin/env python3

from qe_gpu import QeGpu
from openmpi import OpenMPI

qe = Qe(
    prefix = '../run/QE',
    input  = '../input/QE/Si_512.in', 
    mpi    = [ 
        'lib'     : 'impi', 
        'affiniy' : 'scatter', 
        'verbose' : 1 
    ],  
    count = 3 
)

qe.getopt()
qe.info()
qe.build()
qe.run()
qe.summary()
