#!/usr/bin/env python3

from iozone import Iozone

iozone = Iozone(prefix = '../run/IOZONE') 

iozone.build()
iozone.run() 
iozone.summary()
