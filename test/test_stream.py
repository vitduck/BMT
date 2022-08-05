#!/usr/bin/env python3

from stream import Stream

stream = Stream(
    prefix = '../run/STREAM/ORG' )

stream.getopt() 
stream.info() 
stream.download() 
stream.build()
stream.run() 

# scan affinity/thread 
#  for affinity in ['close', 'spread']: 
    #  omp = 4

    #  while omp <= int(stream.host['CPUs']): 
        #  stream.affinity = affinity
        #  stream.omp      = omp

        #  stream.run() 
        #  omp += 4 

stream.summary() 
