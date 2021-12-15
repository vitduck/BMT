#!/usr/bin/env python3

from qe import Qe

qe = Qe(
    prefix = '../run/QE', 
    input  = '../input/QE/Si_512.in' )

qe.info()
qe.build()

for nodes in [1]: 
    for ntasks in [2, 4, 8]:
        for omp in [1, 2, 4, 8]:
            qe.nodes  = nodes
            qe.ntasks = ntasks
            qe.omp    = omp

            qe.run()

qe.summary()
