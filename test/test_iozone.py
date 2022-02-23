#!/usr/bin/env python3

from pprint import pprint
from iozone import Iozone

iozone = Iozone(
    count  = 3, 
    prefix = '../run/IOZONE' ) 

iozone.info()
iozone.build()
iozone.run() 
iozone.summary()
