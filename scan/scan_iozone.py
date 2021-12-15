#!/usr/bin/env python3

from iozone import Iozone

io = Iozone(
    prefix = '../run/IOZONE', 
    size   = '1G' )

io.info()
io.build()

for nodes in [1, 2]: 
    for record in ['64k', '256K']: 
        for thread in [1, 2, 4]:
            io.nodes  = nodes
            io.record = record 
            io.thread = thread

            io.run()

io.summary()
