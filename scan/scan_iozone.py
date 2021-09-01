#!/usr/bin/env python3

from iozone import Iozone

io = Iozone(
    prefix          = '../run/IOZONE', 
    thread_per_host = 32)

io.build()

for record in ['16k', '64k', '256k', '512k', '1024k']: 
    for thread in [1, 2, 4, 8, 16, 32]:
        io.record = record 
        io.thread = thread

        io.run()

io.summary()
