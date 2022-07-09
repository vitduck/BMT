#!/usr/bin/env python3

from qe_gpu  import QeGpu
from openmpi import OpenMPI

qe = QeGpu(
    prefix     = '../run/QE', 
    input      = '../input/QE/Ausurf_112.in', 
    npool      = 2, 
    cuda_aware = True, 
    mpi        = OpenMPI(
        bind = 'none', 
        numa = True )) 

qe.getopt()
qe.info()
qe.download()
qe.build()
qe.run()
qe.summary()
