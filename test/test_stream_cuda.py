#!/usr/bin/env python3

from stream_cuda import StreamCuda

stream = StreamCuda(
    count  = 3, 
    prefix = '../run/STREAM/CUDA' )

stream.info()
stream.build()
stream.run() 
stream.summary()
