#!/usr/bin/env python3

from stream_cuda import StreamCuda

stream = StreamCuda(
    prefix = '../run/STREAM/CUDA' )

stream.info()
stream.download()
stream.build()
stream.run() 
stream.summary()
