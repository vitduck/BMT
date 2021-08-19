#!/usr/bin/env python3

from stream_omp import StreamOmp

stream = StreamOmp(
    prefix = '../run/STREAM/OMP')

stream.build()
stream.run() 
stream.summary()
