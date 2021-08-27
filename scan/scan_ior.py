#!/usr/bin/env python3

from ior import Ior

ior = Ior(
    prefix = '../run/IOR' )

ior.build()

for nodes in [2]: 
    for ntasks in [1, 2, 4, 8]: 
        for block in ['16m', '64m', '256m']:
            ior.nodes  = nodes 
            ior.ntasks = ntasks
            ior.block  = block

            ior.run() 

ior.summary()
