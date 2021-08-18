#!/usr/bin/env python3

from iozone import Iozone

io = Iozone(
    prefix = '../run/IOZONE', 
    thread_per_host = 8 )

io.build()

for thread in [1, 2, 4, 8]:
    io.thread = thread

    io.run()

io.summary()
