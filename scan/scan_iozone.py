#!/usr/bin/env python3

from iozone import Iozone

io = Iozone(
    prefix          = '../run/IOZONE', 
    thread_per_host = 4)

io.build()

for size in ['64m', '256m']:
    for record in ['64k', '256K', '1024K']: 
        for thread in [1, 2, 4]:
            io.size   = size
            io.record = record 
            io.thread = thread

            io.run()

io.summary()
