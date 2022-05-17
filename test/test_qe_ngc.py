#!/usr/bin/env python3

from qe_gpu  import QeGpu
from openmpi import OpenMPI

qe = QeGpu(
    prefix = '../run/QE', 
    input  = '../input/QE/Ausurf_112.in', 
    sif    = '../image/qe-6.8.sif', 
    mpi    = OpenMPI() )

qe.getopt()
qe.info()
qe.run()
qe.summary()
