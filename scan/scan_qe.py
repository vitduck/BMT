#!/usr/bin/env python3

from qe import Qe

qe = Qe(
    prefix = '../run/QE', 
    input  = '../input/QE/Si.in')

qe.build()

for nodes in [1, 2]: 
    for ngpus in [2]: 
        for ntasks in [1, 2, 4]:
            if ntasks < ngpus: 
                continue
            for omp in [1, 2, 4]: 
                qe.ngpus  = ngpus 
                qe.ntasks = ntasks
                qe.omp    = omp

                qe.run()

#  qe.summary()
qe.summary(sort=1, order='<')
